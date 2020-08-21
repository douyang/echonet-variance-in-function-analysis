from ast import literal_eval
import cv2
import numpy as np
import math
import os
import pandas as pd

def makeDirectories(dataPath, vidName):
  framesPath = os.path.join(dataPath, "frames/")
  maskPath = os.path.join(dataPath, "mask/")
  lines = os.path.join(dataPath, "line-orig/")
  stats = os.path.join(dataPath, "stats/")

  if os.path.isdir(framesPath) is False:
    os.mkdir(framesPath)

  if os.path.isdir(maskPath) is False:
    os.mkdir(maskPath)

  if os.path.isdir(lines) is False:
    os.mkdir(lines)

  if os.path.isdir(stats) is False:
    os.mkdir(stats)

def getSpecificFrameAndCrop(dataPath, vidPath, outputPath, frameNumber):
  vidName = os.path.basename(vidPath)
  if (os.path.exists(vidPath)):
    cap = cv2.VideoCapture(vidPath)

    cap.set(1, frameNumber)
    ret, frame = cap.read()

    h, w, c = frame.shape

    makeDirectories(dataPath, vidName)
    # Starting Coords
    x1 = 0
    y1 = 0

    # Ending Coords
    x2 = 112
    y2 = 112

    # Crop
    crop = frame[x1:x2, y1:y2]
    cv2.imwrite(outputPath, crop)

# Gets all the contours for certain image
def obtainContourPoints(path):
  # read image
  img = cv2.imread(path)

  # convert to hsv color space
  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  kernel = np.ones((5,5),np.uint8)

  # set lower and upper bounds on blue color
  lower = (0,90,200)
  upper = (150,255,255)

  # threshold and invert so hexagon is white on black background
  thresh = cv2.inRange(hsv, lower, upper);
  opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
  closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
  erosion = cv2.erode(closing,kernel,iterations = 1)
  dilation = cv2.dilate(erosion,kernel,iterations = 1)
  # blur = cv2.GaussianBlur(closing,(5,5),0)

  # get contours
  result = np.zeros_like(img)
  contours = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  contours = contours[0] if len(contours) == 2 else contours[1]

  # Gets all contour points
  points = []
  for pt in contours:
      for i in pt:
        for coord in i:
          points.append(coord.tolist())
  
  # Resets
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  return points

# Finds points for main contour line
def getTopAndBottomCoords(points):
  # Minimum and Maximum Y Coord
  maxY = max(points, key = lambda point: point[1])
  minY = min(points, key = lambda point: point[1])

  # MinY and MaxY With the limits
  minYWith5 = minY[1] + 5
  maxYWithout5 = maxY[1] - 5

  # Creating these arrays
  minYWith5Arr = []
  maxYWithout5Arr = []

  # Finding these points
  for point in points:
    if point[1] == minYWith5:
      minYWith5Arr.append(point)
    elif point[1] == maxYWithout5:
      maxYWithout5Arr.append(point)

  # Average X Coordinates
  averageTopX = round((minYWith5Arr[0][0] + minYWith5Arr[-1][0])/2)
  averageBottomX = round((maxYWithout5Arr[0][0] + maxYWithout5Arr[-1][0])/2)

  # Creating these arrays
  averageTopXArr = []
  averageBottomXArr = []

  # Finding these points
  for point in points:
    if point[0] == averageTopX:
      averageTopXArr.append(point)
    elif point[0] == averageBottomX:
      averageBottomXArr.append(point)

  # Sorting Arrs
  averageTopXArr.sort(key=lambda point: point[1])
  averageBottomXArr.sort(key=lambda point: point[1])
  averageBottomXArr.reverse()

  # Finding Min Top and Max Botpp,
  TopCoord = averageTopXArr[0]
  BottomCoord = averageBottomXArr[0]

  x1, y1 = TopCoord
  x2, y2 = BottomCoord

  return (x1, y1, x2, y2)

# Create the 20 equally spaced points
def getWeightedAveragePoints(x1, y1, x2, y2, number):
  weighted_avg = []

  for n in range(1, number+1, 1):
    x_perpendicular = (((n*x1)+(number+1-n)*(x2))/(number+1))
    y_perpendicular = (((n*y1)+(number+1-n)*(y2))/(number+1))
    weighted_avg.append([x_perpendicular, y_perpendicular])

  return weighted_avg

# Intercept slope
def calcExpectedIntercept(x, y, slope):
  return slope*x - y

def splitPoints(x1, y1, x2, y2, slope, points):
  # Calculate perpendicular slope
  perp_slope = -1/slope
  val = 0

  # Partitions grid to two halvess
  val = min(calcExpectedIntercept(x1, y1, slope), calcExpectedIntercept(x2, y2, slope))
  
  # Points on lower half
  lowerIntercept = []
  # Points on higher half
  higherIntercept = []

  # Partitions points into two halves
  for point in points:
    x, y = point
    x = int(x)
    y = int(y)
    expectedVal = calcExpectedIntercept(x, y, slope)

    if expectedVal > val:
      higherIntercept.append([x, y])
    else:
      lowerIntercept.append([x, y])
    
  # Gets rid of initial points
  if [x1, y1] in lowerIntercept:
    index = lowerIntercept.index([x1, y1])
    lowerIntercept = lowerIntercept[index:] + lowerIntercept[0:index]
    lowerIntercept = lowerIntercept[1:-1]
  else:
    index = higherIntercept.index([x1, y1])
    higherIntercept = higherIntercept[index:] + higherIntercept[0:index]
    higherIntercept = higherIntercept[1:-1]

  lowerIntercept = [[x1, y1]] + lowerIntercept
  higherIntercept = [[x2, y2]] + higherIntercept

  return (lowerIntercept, higherIntercept)

# Distance Between 2 Pointss
def getDistance(point1, point2):
  return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

# Slope between points 
def getSlope(point1, point2):
  if ((point1[0] == point2[0])):
    return -333
  return (point1[1] - point2[1])/(point1[0] - point2[0])

def findCorrespondingMaskPoints(weighted_avg, lowerIntercept, higherIntercept, x1, y1, x2, y2, slope):
  # Calculate perpendicular slope
  perp_slope = -1/slope

  # Indexing
  lowerIndex = 0
  higherIndex = 0

  # Make sure its from top to bottom direction
  if (weighted_avg[-1][0] + weighted_avg[-1][1]) < (weighted_avg[0][0] + weighted_avg[0][1]):
    weighted_avg = weighted_avg[::-1]

  # Make sure its from top to bottom direction
  if getDistance(weighted_avg[0], higherIntercept[0]) > getDistance(weighted_avg[0], higherIntercept[-1]):
      higherIntercept = higherIntercept[::-1]

  # Make sure its from top to bottom direction
  if getDistance(weighted_avg[0], lowerIntercept[0]) > getDistance(weighted_avg[0], lowerIntercept[-1]):
      lowerIntercept = lowerIntercept[::-1]

  higherInterceptAveragePoints = []
  lowerInterceptAveragePoints = []

  for averagePoint in weighted_avg:
    condition = True
    while condition:
      point = higherIntercept[higherIndex]
      new_slope = getSlope(point, averagePoint)
      higherIndex += 1


      if new_slope>perp_slope:
        higherInterceptAveragePoints.append(point)
        condition = False

  for averagePoint in weighted_avg:
    condition = True
    while condition:
      point = lowerIntercept[lowerIndex]
      new_slope = getSlope(point, averagePoint)
      lowerIndex += 1

      if new_slope<perp_slope:
        lowerInterceptAveragePoints.append(point)
        condition = False
  
  return (lowerInterceptAveragePoints, higherInterceptAveragePoints)

def volumeSimpsonMethodCalc(x1, y1, x2, y2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints):
  # Long axis length and perp initialzation
  distance = getDistance([x1, y1], [x2, y2])
  parallelSeperationDistance = distance/(number + 1)

  # Simpson Volume Methods
  volume = 0

  for i in range(len(lowerInterceptAveragePoints)):
    diameter = getDistance(lowerInterceptAveragePoints[i], higherInterceptAveragePoints[i])
    radius = diameter/2
    diskVolume = math.pi * radius**2 * parallelSeperationDistance
    volume += diskVolume

  return volume

def volumeSingleEllipsoidMethodCalc(x1, y1, x2, y2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints):
  # Long axis length
  long_axis_length = getDistance([x1, y1], [x2, y2])
  parallelSeperationDistance = distance/(number + 1)

  # Simpson Area Method
  area = 0

  for i in range(len(lowerInterceptAveragePoints)):
    length = getDistance(lowerInterceptAveragePoints[i], higherInterceptAveragePoints[i])
    diskArea = length * parallelSeperationDistance
    area += diskArea

  # Volume Calc
  volume = 0.85 * area**2 / length

  return volume

def volumeBiplaneAreaMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints):
  # Long axis Length
  long_axis_length = getDistance([x1, y1], [x2, y2])

  # Storing all perp lengths
  lengthArr = []

  for i in range(len(lowerInterceptAveragePoints)):
    length = getDistance(lowerInterceptAveragePoints[i], higherInterceptAveragePoints[i])
    lengthArr.append(length)

  # 3 diff heuristics
  averageLength = sum(lengthArr)/len(lengthArr)
  maxLength = max(lengthArr)
  midLength = lengthArr[len(lengthArr)//2]

  # Volume Calc
  volume = math.pi/6 * averageLength**2 * long_axis_length

  return volume

def volumeBulletMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints):
  # Long axis Length
  long_axis_length = getDistance([x1, y1], [x2, y2])

  # Mid Values
  midIndex = len(lengthArr)//2
  midLength = getDistance(lowerInterceptAveragePoints[midIndex], higherInterceptAveragePoints[midIndex])

  # Volume Calc
  volume = 5/6 * midLength**2 * long_axis_length

  return volume

def calculateVolume(path, number, method = "Simpson"):
  try:
    points = obtainContourPoints(path)

    x1, y1, x2, y2 = getTopAndBottomCoords(points)
    mainLineSlope = getSlope([x1, y1], [x2, y2])
    baseAngle = math.atan(mainLineSlope)
    if baseAngle>0:
        baseAngle -= math.pi
    lowerIntercept, higherIntercept = splitPoints(x1, y1, x2, y2, mainLineSlope, points)

    volumes = {}
    x1s = {}
    y1s = {}
    x2s = {}
    y2s = {}
    degrees = {}
  
    # Volumes for all 0 to 5 cases
    for i in range(-5, 6, 1):
      x1, y1 = lowerIntercept[i]
      x2, y2 = higherIntercept[i]

      slope = getSlope([x1, y1], [x2, y2])
      angle = math.atan(slope)

      if angle>0:
        angle -= math.pi
        
      degrees[i] = (baseAngle - angle) * 180/math.pi

      p1Index = points.index([x1, y1])
      p2Index = points.index([x2, y2])

      lowerIndex = min(p1Index, p2Index)
      higherIndex = max(p1Index, p2Index)

      higherInterceptPoints = points[lowerIndex:higherIndex]
      lowerInterceptPoints = points[higherIndex:] + points[:lowerIndex]

      weighted_avg = getWeightedAveragePoints(x1, y1, x2, y2, number)
      lowerInterceptAveragePoints, higherInterceptAveragePoints = findCorrespondingMaskPoints(weighted_avg, lowerInterceptPoints, higherInterceptPoints, x1, y1, x2, y2, slope)
      
      x1s[i] = [x1] + [point[0] for point in lowerInterceptAveragePoints]
      y1s[i] = [y1] + [point[1] for point in lowerInterceptAveragePoints]

      x2s[i] = [x2] + [point[0] for point in higherInterceptAveragePoints]
      y2s[i] = [y2] + [point[1] for point in higherInterceptAveragePoints]


      if  method == "Simpson":
        volumes[i] = volumeSimpsonMethodCalc(x1, y1, x2, y2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Single Ellipsoid":
        volumes[i] = volumeSingleEllipsoidMethodCalc(x1, y1, x2, y2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Biplane Area":
        volumes[i] = volumeBiplaneAreaMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Bullet":
        volumes[i] = volumeBulletMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      else:
        return "Incorrect Method"
    return (volumes, x1s, y1s, x2s, y2s, degrees)
  except:
    return ("", "", "", "", "", "")

def volumeCalc(point1, point2, number, x1, y1, x2, y2):
  distance = getDistance(point1, point2)
  parallelSeperationDistance = distance/(number +1)

  volume = 0

  for i in range(len(x1)):
    diameter = getDistance([x1[i], y1[i]], [x2[i], y2[i]])
    radius = diameter/2
    diskVolume = math.pi * radius**2 * parallelSeperationDistance
    volume += diskVolume
   
  return volume

def calculateVolumeFromCoordinates(df):
  fileNames = []
  x1, y1, x2, y2 = [], [], [], []
  volume = []

  fileNames = []
  for i in range(len(df)):
    fileNames.append(df.iloc[i, 0])
    x1.append(literal_eval(df.iloc[i, 2]))
    y1.append(literal_eval(df.iloc[i, 3]))
    x2.append(literal_eval(df.iloc[i, 4]))
    y2.append(literal_eval(df.iloc[i, 5]))

  volume = []
  indexx = []
  perp_coords = []
  for q in range(len(x1)):
    positive, negative = [], []
    slopes = []
    maxIndex = 0
    positives, negatives = 0, 0

    for i in range(len(x1[q])):
      rise = y2[q][i] - y1[q][i]
      run = x2[q][i] - x1[q][i]
      
      try:
        slope = rise/run
        slopes.append(slope)
        
      except:
        slopes.append(0)

    for i in range(len(slopes)):
      
      if slopes[i] > 0:
        positives += 1
        positive.append(i)
      elif slopes[i] < 0:
        negatives += 1
        negative.append(i)

    if positives == 1:
      maxIndex = positive[0]
    elif negatives == 1:
      maxIndex = negative[0]

    indexx.append(maxIndex)
    perp_x1, perp_y1, perp_x2, perp_y2 = x1[q][maxIndex], y1[q][maxIndex], x2[q][maxIndex], y2[q][maxIndex]
    perp_coords.append([perp_x1, perp_y1, perp_x2, perp_y2])
    x_1, y_1, x_2, y_2 = x1[q][maxIndex+1:], y1[q][maxIndex+1:], x2[q][maxIndex+1:], y2[q][maxIndex+1:]

    lowerPoints, higherPoints = [perp_x1, perp_y1], [perp_x2, perp_y2]
    number = len(x1[q]) - 1
    volume.append([fileNames[q], volumeCalc(lowerPoints, higherPoints, number, x_1, y_1, x_2, y_2)])
  
  vols = {}
  for i,k in zip(volume[0::2], volume[1::2]):
    EDV = max(i[1], k[1])
    ESV = min(i[1], k[1])

    if i[0] not in vols:
      vols[i[0]] = [EDV, ESV]

  volumeArr = []
  for i in vols:
    volumeArr.append([i, vols[i][0], vols[i][1]])

  file_df = pd.DataFrame(volumeArr)

  return file_df

#print(calculateVolume("/content/output/image.png", 20, method = "Simpson")[5])
# print(calculateVolume("/content/output/image.png", method = "Single Ellipsoid"))
# print(calculateVolume("/content/output/image.png", method = "Biplane Area"))
# print(calculateVolume("/content/output/image.png", method = "Bullet"))