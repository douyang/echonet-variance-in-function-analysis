import os
import cv2
import numpy as np
import math

def makeDirectories(dataPath, vidName):
  if os.path.isdir(dataPath + "frames/") is False:
    os.mkdir(dataPath + "frames/")
    
  if os.path.isdir(dataPath + "frames/" + vidName) is False:
    os.mkdir(dataPath + "frames/" + vidName)

  if os.path.isdir(dataPath + "mask/") is False:
    os.mkdir(dataPath + "mask/")

  if os.path.isdir(dataPath + "mask/" + vidName) is False:
    os.mkdir(dataPath + "frames/" + vidName)

  if os.path.isdir(dataPath + "line-orig/") is False:
    os.mkdir(dataPath + "line-orig/")

  if os.path.isdir(dataPath + "line-orig/" + vidName) is False:
    os.mkdir(dataPath + "line-orig/" + vidName)

def getSpecificFrameAndCrop(dataPath, vidPath, frameNumber):
  vidName = os.path.basename(vidPath)
  if (os.path.exists(vidPath)):
    cap = cv2.VideoCapture(vidPath)

    cap.set(1, frameNumber)
    ret, frame = cap.read()

    outputPath = dataPath + "frames/" + vidName + "/" + str(frameNumber) + ".png"
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

def makeMask(imagePath, outputPath, coordinatePairs):
  image = cv2.imread(imagePath, -1)

  mask = np.zeros(image.shape, dtype=np.uint8)
  roi_corners = np.array([coordinatePairs], dtype=np.int32)
  
  channel_count = image.shape[2]
  ignore_mask_color = (255,)*channel_count
  cv2.fillPoly(mask, roi_corners, ignore_mask_color)

  # apply the mask
  masked_image = cv2.bitwise_and(image, mask)
  
  # save the result
  cv2.imwrite(outputPath, masked_image)

import cv2
import numpy as np
import math

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
          points.append(coord)
  
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

def getXsAndYsWithSlope(higherInterceptPoints, lowerIntercept, slope):
  print(higherInterceptPoints)

# Create the 20 equally spaced points
def getWeightedAveragePoints(x1, y1, x2, y2):
  weighted_avg = []

  for n in range(1, 21, 1):
    x_perpendicular = (((n*x1)+(21-n)*(x2))/21)
    y_perpendicular = (((n*y1)+(21-n)*(y2))/21)
    weighted_avg.append([x_perpendicular, y_perpendicular])

  return weighted_avg

# Intercept slope
def calcExpectedIntercept(x, y, slope):
  return slope*x - y

def splitPoints(x1, y1, x2, y2, slope, points):
  # Calculate perpendicular slope
  perp_slope = -1/slope
  
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

  # Important Mask Points
  higherInterceptAveragePoints = []
  lowerInterceptAveragePoints = []

  # Goes through mask for high side
  for averagePoint in weighted_avg:
    condition = True
    while condition:
      point = higherIntercept[higherIndex]
      new_slope = getSlope(point, averagePoint)
      higherIndex += 1

      if new_slope>perp_slope:
        higherInterceptAveragePoints.append(point)
        condition = False

  # Goes through mask for low side
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

def volumeSimpsonMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints):
  # Long axis length and perp initialzation
  distance = getDistance([x1, y1], [x2, y2])
  parallelSeperationDistance = distance/21

  # Simpson Volume Methods
  volume = 0

  for i in range(len(lowerInterceptAveragePoints)):
    diameter = getDistance(lowerInterceptAveragePoints[i], higherInterceptAveragePoints[i])
    radius = diameter/2
    diskVolume = math.pi * radius**2 * parallelSeperationDistance
    volume += diskVolume

  return volume

def volumeSingleEllipsoidMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints):
  # Long axis length
  long_axis_length = getDistance([x1, y1], [x2, y2])
  parallelSeperationDistance = distance/21

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

def drawLines(path, x1, y1, x2, y2lowerInterceptAveragePoints, higherInterceptAveragePoints):
  image = cv2.imread(path)

  for i in range(len(lowerInterceptAveragePoints)):
    cv2.line(image, tuple(lowerInterceptAveragePoints[i]),  tuple(higherInterceptAveragePoints[i]), (255, 255, 255), 1)
  
  #cv2.line(image, tuple(x1, y1),  tuple(x2, y2), (23, 23, 225), 1)
  cv2.imwrite(outputPath, image)

def calculateVolume(path, method):
  try:
    points = obtainContourPoints(path)
    x1, y1, x2, y2 = getTopAndBottomCoords(points)
    mainLineSlope = getSlope([x1, y1], [x2, y2])
    lowerIntercept, higherIntercept = splitPoints(x1, y1, x2, y2, mainLineSlope, points)
    volumes = {}
    x1s = {}
    y1s = {}
    x2s = {}
    y2s = {}

    # Volumes for all 11 cases
    for i in range(-5, 5, 1):
      x1, y1 = lowerIntercept[i]
      x2, y2 = higherIntercept[i]

      slope = getSlope([x1, y1], [x2, y2])

      lowerInterceptPoints, higherInterceptPoints = splitPoints(x1, y1, x2, y2, slope, points)

      weighted_avg = getWeightedAveragePoints(x1, y1, x2, y2)
      lowerInterceptAveragePoints, higherInterceptAveragePoints = findCorrespondingMaskPoints(weighted_avg, lowerInterceptPoints, higherInterceptPoints, x1, y1, x2, y2, slope)

      x1s[i] = [x1] + [point[0] for point in lowerInterceptAveragePoints]
      y1s[i] = [y1] + [point[1] for point in lowerInterceptAveragePoints]

      x2s[i] = [x2] + [point[0] for point in higherInterceptAveragePoints]
      y2s[i] = [y2] + [point[1] for point in higherInterceptAveragePoints]

      if method == "Simpson":
        volumes[i] = volumeSimpsonMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints)

      elif method == "Single Ellipsoid":
        volumes[i] = volumeSingleEllipsoidMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Biplane Area":
        volumes[i] = volumeBiplaneAreaMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Bullet":
        volumes[i] = volumeBulletMethodCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      else:
        return "Incorrect Method"

  except:
    volumes, x1s, y1s, x2s, y2s = "", "", "", "", ""
    
  return (volumes, x1s, y1s, x2s, y2s)


#print(calculateVolume("/content/output/image.png", method = "Simpson"))
# print(calculateVolume("/content/output/image.png", method = "Single Ellipsoid"))
# print(calculateVolume("/content/output/image.png", method = "Biplane Area"))
# print(calculateVolume("/content/output/image.png", method = "Bullet"))