import os
import operator
from PIL import Image
from functools import reduce
import numpy as np
import pylab
from csv import reader
import pandas as pd
from ast import literal_eval
import matplotlib.pyplot as plt
from PIL import Image
import math
import cv2
import scipy.stats

# Distance Between 2 Points
def getDistance(point1, point2):
  return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def calculateVolume(point1, point2, x1, y1, x2, y2, lineNumber):
  distance = getDistance(point1, point2)
  parallelSeperationDistance = distance/(lineNumber+1)

  volume = 0

  for i in range(len(x1)):
    diameter = getDistance([x1[i], y1[i]], [x2[i], y2[i]])
    radius = diameter/2
    diskVolume = math.pi * radius**2 * parallelSeperationDistance
    volume += diskVolume
   
  return volume

def makeDirectories(dataPath, vidName):
  if os.path.isdir(dataPath + "frames/") is False:
    os.mkdir(dataPath + "frames/")
    
  if os.path.isdir(dataPath + "frames/" + vidName) is False:
    os.mkdir(dataPath + "frames/" + vidName)

  if os.path.isdir(dataPath + "mask/") is False:
    os.mkdir(dataPath + "mask/")

  if os.path.isdir(dataPath + "mask/" + vidName) is False:
    os.mkdir(dataPath + "frames/" + vidName)

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

# Gets all the contours for certain image
def obtainContourPoints(path):
  img = cv2.imread(path)

  # convert to hsv color space
  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  kernel = np.ones((5,5),np.uint8)

  # set lower and upper bounds on blue color
  lower = (0,90,200)
  upper = (150,255,255)

  # threshold and invert so hexagon is white on black background
  thresh = cv2.inRange(hsv, lower, upper)
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
  try:
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

  except:
    x1, y1 = "Couldn't calculate", "Couldn't calculate"
    x2, y2 = "Couldn't calculate", "Couldn't calculate"


  return (x1, y1, x2, y2)

# Create the 20 equally spaced points
def getWeightedAveragePoints(x1, y1, x2, y2, number):
  weighted_avg = []

  for n in range(1, (number+1), 1):
    try:
      x_perpendicular = (((n*x1)+((number+1)-n)*(x2))/(number+1))
      y_perpendicular = (((n*y1)+((number+1)-n)*(y2))/(number+1))
    except:
      x_perpendicular = "Can't calculate"
      y_perpendicular = "Can't calculate"

    weighted_avg.append([x_perpendicular, y_perpendicular])

  return weighted_avg

# Intercept slope
def calcExpectedIntercept(x, y, slope):
  return slope*x - y

def splitPoints(x1, y1, x2, y2, points):
  # Prechosen slope
  try:

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

  except:
    lowerIntercept, higherIntercept = "Can't calculate", "Can't calculate"
  return (lowerIntercept, higherIntercept)

# Distance Between 2 Points
def getDistance(point1, point2):
  try:
    distance = math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
  except:
    distance = "Can't calculate"
  return distance

# Slope between points
def getSlope(point1, point2):
  if ((point1[0] == point2[0])):
    return -333
  return (point1[1] - point2[1])/(point1[0] - point2[0])

def findCorrespondingMaskPoints(weighted_avg, lowerIntercept, higherIntercept, x1, y1, x2, y2):
  # Prechosen slope
  try:
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
  except:
    lowerInterceptAveragePoints, higherInterceptAveragePoints = "Can't calculate", "Can't calculate"
  return (lowerInterceptAveragePoints, higherInterceptAveragePoints)

def volumeCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints, number):
  try:
    distance = getDistance([x1, y1], [x2, y2])
    parallelSeperationDistance = distance/(number+1)

    volume = 0
    for i in range(len(lowerInterceptAveragePoints)):
      diameter = getDistance(lowerInterceptAveragePoints[i], higherInterceptAveragePoints[i])
      radius = diameter/2
      diskVolume = math.pi * radius**2 * parallelSeperationDistance
      volume += diskVolume
  except:
    volume = ""
  return volume

def createArrays(x, y, coordArr):
  try:

    xArr = [x]
    yArr = [y]
    for coordinate in coordArr:
      xArr.append(coordinate[0])
      yArr.append(coordinate[1])
  
  except:
    xArr, yArr = "", ""
  return (xArr, yArr)

def calculateVolume(path, number):
  points = obtainContourPoints(path)
  x1, y1, x2, y2 = getTopAndBottomCoords(points)

  weighted_avg = getWeightedAveragePoints(x1, y1, x2, y2, number)
  lowerIntercept, higherIntercept = splitPoints(x1, y1, x2, y2, points)
  lowerInterceptAveragePoints, higherInterceptAveragePoints = findCorrespondingMaskPoints(weighted_avg, lowerIntercept, higherIntercept, x1, y1, x2, y2)
  volume = volumeCalc(x1, y1, x2, y2, lowerInterceptAveragePoints, higherInterceptAveragePoints, number)
  x1Arr, y1Arr = createArrays(x1, y1, lowerInterceptAveragePoints)
  x2Arr, y2Arr = createArrays(x2, y2, lowerInterceptAveragePoints)

  return (volume, x1Arr, y1Arr, x2Arr, y2Arr)


dataPath = "/Users/ishan/Documents/Stanford/ouyang-data/"
path = dataPath + "CSV/VolumeTracings.csv"

paths, numbers = [], []

df = pd.read_csv(path, low_memory=False)

df = df.astype(str).groupby(['FileName', 'Frame']).agg(','.join).reset_index()
for i in range(len(df)):
  vid = df.iloc[i, 0]
  frame = df.iloc[i, 1]

  frameCapturePath = dataPath + "videos/" + vid
  if os.path.exists(frameCapturePath):
    getSpecificFrameAndCrop(dataPath, frameCapturePath, int(frame))

  path = dataPath + "frames/" + vid + "/" + df.iloc[i, 1] + ".png"
  number = len(literal_eval(df.iloc[i, 2]))

  paths.append([path, vid])
  numbers.append(number)

volumes, calculated_EF = [], []

#Calculate volume based on given video and frame
for i in range(len(paths)):
  pathName = paths[i][0]
  vidName = paths[i][1]
  if os.path.exists(pathName):
    numberValue = numbers[i] - 1
    frameNumber = os.path.basename(pathName)
    volume, x1, y1, x2, y2 = calculateVolume(pathName, numberValue)
    
    volumes.append([vidName, x1, y1, x2, y2, frameNumber, volume])

#new_df = pd.DataFrame(listOfVolumes)

# Calculate the EF
for i,k in zip(volumes[0::2], volumes[1::2]):
  if (i[6] != '') and (k[6] != ''):
    EDV = max(i[6], k[6])
    ESV = min(i[6], k[6])

    ef_calc = ((EDV-ESV)/EDV) * 100
    calculated_EF.append([i[0], ef_calc])

EF = {}

file_df = pd.read_csv(dataPath + "CSV/FileList.csv")
for i in range(len(file_df)):
  fileName = file_df.iloc[i, 0]
  EForig = file_df.iloc[i, 1]
  if fileName not in EF:
    EF[fileName] = ['', '']
  EF[fileName][0] = EForig

for j in range(len(calculated_EF)):
  fileN = calculated_EF[j][0]
  EFcalc = calculated_EF[j][1]

  if fileN not in EF:
    EF[fileN] = ['', '']
  EF[fileN][1] = EFcalc

xList = []
yList = []
fileNames = []

for i in EF:
  if (EF[i][0] != '') and (EF[i][1] != ''):
    xList.append(EF[i][0])
    yList.append(EF[i][1])
    fileNames.append(i)

# Get the line of best fit
x = np.array(xList)
y = np.array(yList)
m, b = np.polyfit(x, y, 1)

# Plot the x and y calculations
plt.plot(x, y, 'o')

plt.plot(x, m*x + b)
#plt.scatter(x, y)
plt.show()

def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return r_value**2

print("R2 is " + rsquared(x, y))