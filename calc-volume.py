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
compareEF = True # comparing EF or timings plots

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
  EF = {}

  framePaths, parallelLinesCount = captureAndMakeCroppedFrames()

  for i in range(len(framePaths)):
    pathName = framePaths[i][0]
    vidName = framePaths[i][1]
    frame = framePaths[i][2]

    numberValue = parallelLinesCount[i]

    volume, x1, y1, x2, y2, slopes = pipeline_functions.calculateVolume(pathName, numberValue, method = methodToUse)
    print(x1)
    if len(x1) is not 0:
      volumes.append([pathName, vidName, frame, volume[0]])

      if vidName not in EF:
        EF[vidName] = {-5: [], -4: [], -3: [], -2: [], -1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
      
      for r in range(-5, 6, 1):
        EF[vidName][r].append(volume[r])

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

  return volumes, flagged_volumes, EF

def compareTimingsWithGroundTruth(method):

  # Gather volumes
  calc, flagged, EF = calculateVolumeAndDrawLines(method)
  
  negative5ESV, negative5EDV, negative4ESV, negative4EDV, negative3ESV, negative3EDV, negative2ESV, negative2EDV, negative1ESV, negative1EDV, zeroESV, zeroEDV, positive1ESV, positive1EDV, positive2ESV, positive2EDV, positive3ESV, positive3EDV, positive4ESV, positive4EDV, positive5ESV, positive5EDV = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  
  negative5, negative4, negative3, negative2, negative1, zero, positive1, positive2, positive3, positive4, positive5 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

  counts = 0

  # Set the differences in EDV and ESV to the dictionary
  for i in range(len(file_df)):

    vid = file_df.iloc[i, 0]
    truth_EDV = file_df.iloc[i, 2]
    truth_ESV = file_df.iloc[i, 3]

    if vid in EF:
      for angleChange in EF[vid]:
        EDV = max(EF[vid][angleChange])
        ESV = min(EF[vid][angleChange])

        if compareEF is False:
          EF[vid][angleChange] = [abs(truth_ESV-ESV), abs(truth_EDV-EDV)]
        else:
          ef = ((EDV-ESV)/EDV) * 100
          EF[vid][angleChange] = ef
  
  # Sum all the EDV and ESV for each angle
  if compareEF is False:
    for i in EF:
      negative5ESV += EF[i][-5][0]
      negative5EDV += EF[i][-5][1]

      negative4ESV += EF[i][-4][0]
      negative4EDV += EF[i][-4][1]

      negative3ESV += EF[i][-3][0]
      negative3EDV += EF[i][-3][1]

      negative2ESV += EF[i][-2][0]
      negative2EDV += EF[i][-2][1]

      negative1ESV += EF[i][-1][0]
      negative1EDV += EF[i][-1][1]

      zeroESV += EF[i][0][0]
      zeroEDV += EF[i][0][1]

      positive1ESV += EF[i][1][0]
      positive1EDV += EF[i][1][1]

      positive2ESV += EF[i][2][0]
      positive2ESV += EF[i][2][1]
      
      positive3ESV += EF[i][3][0]
      positive3EDV += EF[i][3][1]

      positive4ESV += EF[i][4][0]
      positive4EDV += EF[i][4][1]

      positive5ESV += EF[i][5][0]
      positive5EDV += EF[i][5][1]
      counts += 1

    if counts > 0:
      return [[negative5ESV/counts, negative5EDV/counts], [negative4ESV/counts, negative4EDV/counts], [negative3ESV/counts, negative3EDV/counts], [negative2ESV/counts, negative2EDV/counts], [negative1ESV/counts, negative1EDV/counts], [zeroESV/counts, zeroEDV/counts], [positive1ESV/counts, positive1EDV/counts], [positive2ESV/counts, positive2EDV], [positive3ESV/counts, positive3EDV], [positive4ESV/counts, positive4EDV], [positive5ESV/counts, positive5EDV]], "Box"
    else:
      return [0, 0], "Box"

  else:
    # Append the ground truth EF to the dictionary
    for i in range(len(file_df)):
      if file_df.iloc[i, 0] in EF:
        negative5 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][-5])
        negative4 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][-4])
        negative3 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][-3])
        negative2 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][-2])
        negative1 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][-1])
        zero += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][0])
        positive1 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][1])
        positive2 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][2])
        positive3 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][3])
        positive4 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][4])
        positive5 += abs(file_df.iloc[i, 1] - EF[file_df.iloc[i, 0]][5])
        counts += 1

    if counts > 0:
      return [negative5/counts, negative4/counts, negative3/counts, negative2/counts, negative1/counts, zero/counts, positive1/counts, positive2/counts, positive3/counts, positive4/counts, positive5/counts], "Bar"
    else:
      return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "Bar"

def makePlot(method):
  data_to_plot, dataType = compareTimingsWithGroundTruth(method)
  if dataType is "Box":
    # Create a figure instance
    fig = plt.figure(1, figsize=(9, 6))

    # Create an axes instance
    ax = fig.add_subplot(111)
    ax.set_xticklabels(['-5', '-4','-3','-2','-1','0','1','2','3','4', '5'])
    ax.set_title('ESV and EDV vs Ground Truth (' + method + ")")

    # Create the boxplot
    bp = ax.boxplot(data_to_plot[:-3])

    # Save the figure
    exportPath = dataPath + "stats/" + method + " - EF.png"
    fig.savefig(dataPath + method + '.png', bbox_inches='tight')
  
  elif dataType is "Bar":
    x=['-5', '-4','-3','-2','-1','0','1','2','3','4', '5']
    y = data_to_plot

    plt.bar(x,y)
    plt.xlabel('Angle Shifts')
    plt.ylabel("Average Differences")
    plt.title("EF vs Ground Truth (" + method + ")")

    exportPath = dataPath + "stats/" + method + " - timing.png"
    plt.savefig(exportPath)
    plt.show()

makePlot("Simpson")
#makePlot("Single Ellipsoid")
#makePlot("Biplane Area")
#makePlot("Bullet")