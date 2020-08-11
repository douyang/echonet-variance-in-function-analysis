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

volumes, calculated_EF = [], []

EF = {}

# Capture and Make Frames + Crop
def captureAndMakeCroppedFrames(dataframe):
  for i in len(dataframe):
    vid = dataframe.iloc[i, 0]
    frameNumber = dataframe.iloc[i, 1]

    frameCapturePath = dataPath + "videos/" + vid
    
    if (os.path.exists(frameCapturePath)):
      pipeline_functions.getSpecificFrameAndCrop(dataPath, frameCapturePath, int(frameNumber))

def gatherPathsAndFrameData(dataPath, dataframe):
  paths, numbers = [], []

  for i in range(len(dataframe)):
    vid = dataframe.iloc[i, 0]

    frameOutputPath = dataPath + "frames/" + vid

    path = frameOutputPath + "/" + dataframe.iloc[i, 1] + ".png"
    numberOfParallelLines = len(literal_eval(dataframe.iloc[i, 2])) - 1

    paths.append([path, vid])
    numbers.append(numberOfParallelLines)
  
  return paths, numbers

#Calculate volume based on given video and frame
def calculateVolumeFromData(dataPath, dataframe, methodToUse):
  framePaths, parallelLinesCount = gatherPathsAndFrameData(dataPath, dataframe)

  for i in range(len(framePaths)):
    pathName = framePaths[i][0]
    vidName = framePaths[i][1]

    if os.path.exists(pathName):
      numberValue = parallelLinesCount[i]
      frameNumber = os.path.basename(pathName)
      outputPath = dataPath + "line-orig/" + vidName + "/" + str(frameNumber)

      volume, x1, y1, x2, y2 = pipeline_functions.calculateVolume(pathName, numberValue, methodToUse)
      
      try:
        image = cv2.imread(pathName)
        for k in range(len(x1)):
          cv2.line(image, (x1[0][k], y1[0][k]), (x2[0][k], y2[0][k]), (255, 255, 255), 1)
          
        cv2.imwrite(outputPath, image)
        
      except:
        continue
      # volumes.append([vidName, x1, y1, x2, y2, frameNumber, volume])
  

calculateVolumeFromData(dataPath, df, "Biplane Area")

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