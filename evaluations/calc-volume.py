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

makeFrames = False # generate frames and lines

dataPath = "/Users/ishan/Documents/Stanford/ouyang-data/"
path = os.path.join(dataPath, "CSV/", "VolumeTracings.csv")

df = pd.read_csv(path, low_memory=False)
file_df = pd.read_csv(os.path.join(dataPath, "CSV/", "FileList.csv"))

df = df.astype(str).groupby(['FileName', 'Frame']).agg(','.join).reset_index()

# Capture and Make Frames + Crop
def captureAndMakeCroppedFrames():
  paths, numbers = [], []

  for i in range(len(df)):
    vid = df.iloc[i, 0]
    frameNumber = df.iloc[i, 1]

    frameCapturePath = os.path.join(dataPath, "videos/",  vid)
    numberOfParallelLines = len(literal_eval(df.iloc[i, 2])) - 1

    if (os.path.exists(frameCapturePath)):
      outputPath = os.path.join(dataPath, "frames/", vid + "_" + str(frameNumber) + ".png")

      if makeFrames is True:
        pipeline_functions.getSpecificFrameAndCrop(dataPath, frameCapturePath, outputPath, int(frameNumber))

      paths.append([outputPath, vid, frameNumber])
      numbers.append(numberOfParallelLines)

  return paths, numbers

# Evaluate functions based on captureAndMakeCroppedFrames() function's returned data
def calculateVolumeAndDrawLines(methodToUse):
  volumes, flagged_volumes = [], []
  volumes_dict, angle_changes = {}, {}

  framePaths, parallelLinesCount = captureAndMakeCroppedFrames()

  for i in range(len(framePaths)):
    pathName = framePaths[i][0]
    vidName = framePaths[i][1]
    frame = framePaths[i][2]

    numberValue = parallelLinesCount[i]

    volume, x1, y1, x2, y2, angles = pipeline_functions.calculateVolume(pathName, numberValue, method = methodToUse)
    if len(x1) is not 0:
      volumes.append([pathName, vidName, frame, volume[0]])

      if vidName not in volumes_dict:
        volumes_dict[vidName] = {-5: [], -4: [], -3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
        angle_changes[vidName] = {-5: [], -4: [], -3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

      for r in range(-5, 6, 1):
        volumes_dict[vidName][r].append(volume[r])
        angle_changes[vidName][r].append(angles[r])

      if makeFrames == True:
        outputPath = os.path.join(dataPath, "line-orig/", vidName + "_" + frame + ".png")

        image = cv2.imread(pathName)

        for k in range(len(x1[0])):
          if k is 0:
            longLine1stCoords = (x1[0][k], y1[0][k])
            longLine2ndCoords = (x2[0][k], y2[0][k])
          else:
            cv2.line(image, (x1[0][k], y1[0][k]), (x2[0][k], y2[0][k]), (255, 255, 255), 1)
          
          cv2.line(image, longLine1stCoords, longLine2ndCoords, (31, 55, 145), 3) # Drawing the long line in different color

        cv2.imwrite(outputPath, image)
    else:
      flagged_volumes.append([pathName, vidName, frame])

  return volumes, flagged_volumes, volumes_dict, angle_changes

def compareESVAndEFV(methodToUse):
  vol, flagged_vol, volumes, angle_changes = calculateVolumeAndDrawLines(methodToUse)

  x_esv, x_edv, angle_edv, angle_esv = [], [], [], []

  truth_df = pipeline_functions.calculateVolumeFromCoordinates(df)
  # Set the differences in EDV and ESV to the dictionary
  for i in range(len(truth_df)):
    
    vid = truth_df.iloc[i, 0]
    truth_EDV = truth_df.iloc[i, 1]
    truth_ESV = truth_df.iloc[i, 2]
    
    if vid in volumes:
      for angleChange in volumes[vid]:
        EDV = max(volumes[vid][angleChange])
        ESV = min(volumes[vid][angleChange])

        change_EDV = max(angle_changes[vid][angleChange])
        change_ESV = min(angle_changes[vid][angleChange])
        
        volumes[vid][angleChange] = [abs(((truth_ESV-ESV)/ESV)*100), abs(((EDV-truth_EDV)/truth_EDV)*100), change_EDV, change_ESV]

  for i in volumes:
    for r in volumes[i]:
      x_esv.append(volumes[i][r][0])
      x_edv.append(volumes[i][r][1])
      angle_esv.append(volumes[i][r][2])
      angle_edv.append(volumes[i][r][3])

  return x_esv, x_edv, angle_esv, angle_edv

def generateScatterPlot(method, volumeType):
  x_esv, x_edv, y_esv, y_edv = compareESVAndEFV(method)

  fig = plt.figure()

  if volumeType == "ESV":
    plt.scatter(y_esv, x_esv)
    plt.xlabel('Angle Changes', fontsize=18)
    plt.ylabel('Percent Change in ESV', fontsize=16)
    fig.savefig(dataPath + 'stats/ESV Changes.jpg')
  
  elif volumeType == "EDV":
    plt.scatter(y_edv, x_edv)
    plt.xlabel('Angle Changes', fontsize=18)
    plt.ylabel('Percent Change in EDV', fontsize=16)
    fig.savefig(dataPath + 'stats/EDV Changes.jpg')

  plt.show()

generateScatterPlot("Simpson", "ESV")