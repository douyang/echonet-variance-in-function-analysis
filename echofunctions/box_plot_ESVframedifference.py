"""Assessing difference in ejection
fraction with changes in ESV timings"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import operator
import config
import loader
from algorithms import funcs as funcs
from algorithms import volume_tracings_calculations as tracings
from algorithms import normalizations as normalize
import collections
import cv2
from ast import literal_eval
from tqdm import tqdm

def sortFrameVolumeTracings():
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  print("\nCalculatng ground truth volumes from VolumeTracings")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0] + ".avi"

    x1 = list(literal_eval(df.iloc[i, 2])) # x1 coords
    y1 = list(literal_eval(df.iloc[i, 3])) # y1 coords
    x2 = list(literal_eval(df.iloc[i, 4])) # x2 coords
    y2 = list(literal_eval(df.iloc[i, 5])) # y2 coords
    
    number = len(x1) - 1

    maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(x1, y1, x2, y2)

    if number < 22:
      ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      if videoName not in calculatedVolumeFromGroundTruth:
        calculatedVolumeFromGroundTruth[videoName] = []
      
      calculatedVolumeFromGroundTruth[videoName].append(ground_truth_volume)
  return calculatedVolumeFromGroundTruth

# Return dictionary of volume data from FileList
def sortVolumesFromFileList(root=config.CONFIG.DATA_DIR):
  givenTrueDict={}

  df = pd.read_csv(os.path.join(root, "FileList.csv"), ) # reading in FileList.csv

  print("\nGathering volumes from FileList")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

# Returns dictionary with calculated volumes (received from CSV)
def getCalculationsFromCSV(CSV_NAME, frameDifference):
  root, _ = loader.dataModules() # get path data
  calculatedVolumes = {}

  df = pd.read_csv(os.path.join(root, "CSVs", CSV_NAME)) # reading in CSV
  df = df.astype(str).groupby(['videoName']).agg(','.join).reset_index() # group based on file name

  print("\nGathering volumes from CSV calculations")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    currentFrameDifference = -frameDifference - 1 # starts at frame difference
    videoName = df.iloc[i, 0] # name of video
    
    for frame in range((frameDifference * 2) + 1):
      currentFrameDifference += 1
      trueEDV = float(df.iloc[i, 2]) # ESV calculation
      calculatedESV = float(df.iloc[i, frame + 3]) # ESV calculation

      if videoName not in calculatedVolumes:
        calculatedVolumes[videoName] = {}
      if currentFrameDifference not in calculatedVolumes[videoName]:
        calculatedVolumes[videoName][currentFrameDifference] = [calculatedESV, trueEDV]
    
  return calculatedVolumes

# Compare volumes using calculated erosion and dilation iterations against FileList or VolumeTracings
def compareVolumePlot(CSV_NAME="esvTimingSweeps.csv", method="Method of Disks", volumeType="EF",
                      fromFile="VolumeTracings", frameDifference=5, root=config.CONFIG.DATA_DIR):
  
  all_volumes = getCalculationsFromCSV(CSV_NAME, frameDifference)

  if fromFile is "VolumeTracings":
    true_volumes = sortFrameVolumeTracings()
  else:
    true_volumes = sortVolumesFromFileList()

  changesInVolumesDict = {}
  for frame in range(-frameDifference, frameDifference + 1, 1):
    changesInVolumesDict[frame] = []

  for videoName in true_volumes:
    volumeData = true_volumes[videoName]

    ground_truth_ESV = min(volumeData) # true ESV value
    ground_truth_EDV = max(volumeData) # true EDV value
    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100 # true EF value (calculated)

    if videoName in all_volumes:
      for r in range(-frameDifference, frameDifference + 1, 1):
        volumes = all_volumes[videoName][r] # volumes of given iteration

        EDV = volumes[1] # calculated EDV for given iteration
        ESV = volumes[0] # calculated ESV for given iteration
        EF = (1 - (ESV/ground_truth_EDV)) * 100 # calculated EF for given iteration
        
        diff_EF = ((EF - ground_truth_EF)/ground_truth_EF) * 100 # difference in calculated EF and true EF
        diff_EDV = ((EDV-ground_truth_EDV)/ground_truth_EDV) * 100 # difference in calculated EDV and true EDV
        diff_ESV = ((ESV-ground_truth_ESV)/ground_truth_ESV) * 100 # difference in calculated ESV and true ESV
        
        if volumeType is "EF":
          changesInVolumesDict[r].append(diff_EF)
        elif volumeType is "ESV":
          changesInVolumesDict[r].append(diff_ESV)
        elif volumeType is "EDV":
          changesInVolumesDict[r].append(diff_EDV)

  print(changesInVolumesDict[10])
  createBoxPlot(changesInVolumesDict, volumeType)

# Create box plot by calling functions and graphing data
def createBoxPlot(differenceInVolumes, volumeType):
  
  # figure related code
  loader.latexify()
  fig, ax = plt.subplots()
  ax.boxplot(differenceInVolumes.values(), showfliers=False)
  ax.set_xticklabels(differenceInVolumes.keys())
  
  #ax.set_title('Difference in Calculated ' + volumeType + ' against ' + fromFile + ' using Erosion and Dilation')
  ax.set_xlabel('Number of frames off from true ESV')

  if volumeType is "ESV" or volumeType is "EDV":
    ax.set_ylabel('% Change in ' + volumeType)
  else:
    ax.set_ylabel('% Change in Ejection Fraction')

  # show plot
  plt.show()

compareVolumePlot(CSV_NAME="esvTimingSweeps.csv", method="Method of Disks", volumeType="EF",
                      fromFile="VolumeTracings", frameDifference=15)