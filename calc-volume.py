import pandas as pd
import cv2
import numpy as np
import math
import os

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

def splitPoints(x1, y1, x2, y2, points):
  # Prechosen slope
  slope = (y2-y1)/(x2-x1)
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
  
  return (lowerIntercept, higherIntercept)

# Distance Between 2 Points
def getDistance(point1, point2):
  return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

# Slope between points
def getSlope(point1, point2):
  if ((point1[0] == point2[0])):
    return -333
  return (point1[1] - point2[1])/(point1[0] - point2[0])

def findCorrespondingMaskPoints(weighted_avg, lowerIntercept, higherIntercept, x1, y1, x2, y2):
  # Prechosen slope
  slope = (y2-y1)/(x2-x1)
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

def volumeCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints):
  distance = getDistance([x1, y1], [x2, y2])
  parallelSeperationDistance = distance/21

  volume = 0
  print(lowerInterceptAveragePoints)
  for i in range(len(lowerInterceptAveragePoints)):
    diameter = getDistance(lowerInterceptAveragePoints[i], higherInterceptAveragePoints[i])
    radius = diameter/2
    diskVolume = math.pi * radius**2 * parallelSeperationDistance
    volume += diskVolume

  return volume

def calculateVolume(path):
  points = obtainContourPoints(path)
  x1, y1, x2, y2 = getTopAndBottomCoords(points)

  weighted_avg = getWeightedAveragePoints(x1, y1, x2, y2)
  lowerIntercept, higherIntercept = splitPoints(x1, y1, x2, y2, points)
  lowerInterceptAveragePoints, higherInterceptAveragePoints = findCorrespondingMaskPoints(weighted_avg, lowerIntercept, higherIntercept, x1, y1, x2, y2)
  print(lowerIntercept)
  volume = volumeCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints)

  return volume


dataPath = "/Users/ishan/Documents/Stanford/ouyang-data/"
path = dataPath + "CSV/VolumeTracings.csv"

def removeDuplicateRows(volume_tracings_path):
  vol_df = pd.read_csv(volume_tracings_path, low_memory=False)
  
  # Only filename and frame number from VolumeTracings
  vol_df = vol_df.drop_duplicates(['FileName', 'Frame'], keep='first')

  return vol_df


df = removeDuplicateRows(path)

# Create arranged order array in format [filename, frame number]
arrangedOrder, listOfVolumes = [], []
for i in range(len(df)):
  fileNames = df.iloc[i, 0]
  frameNumbers = df.iloc[i, 5]

  arrangedOrder.append([fileNames, frameNumbers])


#Calculate volume based on given video and frame
i = 4

for orderedPair in arrangedOrder:
  
  vidName = orderedPair[0]
  frameNumber = orderedPair[1]
  inputFramePath = dataPath + "frames/crop/" + vidName + "/frame" + str(frameNumber) + ".png"
  try:
    volume = calculateVolume(inputFramePath)
    
    if (i % 2) is 0:
      listOfVolumes.append([vidName, frameNumber, volume, "EDV"])
    else:
      listOfVolumes.append([vidName, frameNumber, volume, "ESV"])
    
  except:
    if (i % 2) is 0:
      listOfVolumes.append([vidName, frameNumber, "Couldn't calculate", "EDV"])
    else:
      listOfVolumes.append([vidName, frameNumber, "Couldn't calculate", "ESV"])
    
  i = i + 1

#Create and export dataframe to CSV
new_df = pd.DataFrame(listOfVolumes)
new_df.columns = ['FileName', 'Frame', 'Volume', "State"]
new_df.to_csv(dataPath + 'volume.csv')
