import pipeline_functions
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

dataPath = "/Users/ishan/Documents/Stanford/ouyang-data/"
path = dataPath + "CSV/VolumeTracings.csv"

df = pd.read_csv(path, low_memory=False)
file_df = pd.read_csv(dataPath + "CSV/FileList.csv")

df = df.astype(str).groupby(['FileName', 'Frame']).agg(','.join).reset_index()

# Capture and Make Frames + Crop
def captureAndMakeCroppedFrames():
  for i in range(len(df)):
    vid = df.iloc[i, 0]
    frameNumber = df.iloc[i, 1]

    frameCapturePath = dataPath + "videos/" + vid
    
    if (os.path.exists(frameCapturePath)):
      pipeline_functions.getSpecificFrameAndCrop(dataPath, frameCapturePath, int(frameNumber))

# Gather all paths, frames, and vision data for evaluating functions
def gatherPathsAndFrameData():
  #captureAndMakeCroppedFrames(dataframe)
  paths, numbers = [], []

  for i in range(len(df)):
    vid = df.iloc[i, 0]
    frame = df.iloc[i, 1]

    frameOutputPath = dataPath + "frames/" + vid

    path = frameOutputPath + "/" + frame + ".png"
    numberOfParallelLines = len(literal_eval(df.iloc[i, 2])) - 1

    if os.path.exists(path):
      paths.append([path, vid, frame])
      numbers.append(numberOfParallelLines)
  
  return paths, numbers

# Evaluate functions based on gatherPathsAndFrameData() function's returned data
def calculateVolumeAndDrawLines(methodToUse, drawLines = True):
  volumes, flagged_volumes = [], []
  EF = {}

  framePaths, parallelLinesCount = gatherPathsAndFrameData()

  for i in range(len(framePaths)):
    pathName = framePaths[i][0]
    vidName = framePaths[i][1]
    frame = framePaths[i][2]

    numberValue = parallelLinesCount[i]

    volume, x1, y1, x2, y2 = pipeline_functions.calculateVolume(pathName, numberValue, method = methodToUse)
    if len(x1) is not 0:
      volumes.append([pathName, vidName, frame, volume[0]])

      if vidName not in EF:
        EF[vidName] = {-5: [], -4: [], -3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
      
      for r in range(-5, 6, 1):
        EF[vidName][r].append(volume[r])

      if drawLines == True:
        outputPath = dataPath + "line-orig/" + vidName + "/" + frame + ".png"

        image = cv2.imread(pathName)

        for k in range(len(x1[0])):
          if k is 0:
            cv2.line(image, (x1[0][k], y1[0][k]), (x2[0][k], y2[0][k]), (31, 55, 145), 5)
          else:
            cv2.line(image, (x1[0][k], y1[0][k]), (x2[0][k], y2[0][k]), (255, 255, 255), 1)
          
        cv2.imwrite(outputPath, image)
    else:
      flagged_volumes.append([pathName, vidName, frame])

  return volumes, flagged_volumes, EF

def compareWithGroundTruth(method, shouldDrawLines=True):

  # Gather volumes
  calc, flagged, EF = calculateVolumeAndDrawLines(method, shouldDrawLines)
  
  differences = {}
  negative5, negative4, negative3, negative2, negative1, zero, positive1, positive2, positive3, positive4, positive5 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  
  counts = 0

  # Append the calculated EF to the dictionary
  for k in EF:
    if k not in differences:
      differences[k] = {-5: [], -4: [], -3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

    for angleChange in EF[k]:
      EDV = max(EF[k][angleChange])
      ESV = min(EF[k][angleChange])

      ef = ((EDV-ESV)/EDV) * 100

      differences[k][angleChange] = ef
  
  # Append the ground truth EF to the dictionary
  for i in range(len(file_df)):
    if file_df.iloc[i, 0] in differences:
      negative5 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][-5])
      negative4 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][-4])
      negative3 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][-3])
      negative2 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][-2])
      negative1 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][-1])
      zero = abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][0])
      positive1 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][1])
      positive2 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][2])
      positive3 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][3])
      positive4 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][4])
      positive5 += abs(file_df.iloc[i, 1] - differences[file_df.iloc[i, 0]][5])
      counts += 1

  try:
    return [negative5/counts, negative4/counts, negative3/counts, negative2/counts, negative1/counts, zero/counts, positive1/counts, positive2/counts, positive3/counts, positive4/counts, positive5/counts]
  except:
    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def makeHistogram(method):
  x=['-5', '-4','-3','-2','-1','0','1','2','3','4', '5']
  y = compareWithGroundTruth(method)

  print(y)
  plt.bar(x,y)
  plt.xlabel('Angle Shifts')
  plt.ylabel("Average Differences")
  plt.title(method)
  plt.show()

makeHistogram("Simpson")
makeHistogram("Single Ellipsoid")
makeHistogram("Biplane Area")
makeHistogram("Bullet")
# # Calculate the EF
# for i,k in zip(volumes[0::2], volumes[1::2]):
#   if (i[6] != '') and (k[6] != ''):
#     EDV = max(i[6], k[6])
#     ESV = min(i[6], k[6])
#     ef_calc = ((EDV-ESV)/EDV) * 100
#     calculated_EF.append([i[0], ef_calc])

# # Organizing EF Calculations by Name
# for i in range(len(file_df)):
#   fileName = file_df.iloc[i, 0]
#   EForig = file_df.iloc[i, 1]
#   if fileName not in EF:
#     EF[fileName] = ['', '']
#   EF[fileName][0] = EForig

# for j in range(len(calculated_EF)):
#   fileN = calculated_EF[j][0]
#   EFcalc = calculated_EF[j][1]

#   if fileN not in EF:
#     EF[fileN] = ['', '']
#   EF[fileN][1] = EFcalc

# # Generating scatter plots
# xList = []
# yList = []
# fileNames = []

# for i in EF:
#   if (EF[i][0] != '') and (EF[i][1] != ''):
#     xList.append(EF[i][0])
#     yList.append(EF[i][1])
#     fileNames.append(i)

# # Get the line of best fit
# x = np.array(xList)
# y = np.array(yList)
# m, b = np.polyfit(x, y, 1)

# # Plot the x and y calculations
# plt.plot(x, y, 'o')

# plt.plot(x, m*x + b)
# #plt.scatter(x, y)
# plt.show()

# def rsquared(x, y):
#   slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
#   return r_value**2

# print("r2: ")
# print(rsquared(x, y))