"""Echonet Function Evaluation comparisons of different
methods' angle shifts to compare the volume vs. ground truth"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import config
import loader
from algorithms import funcs as funcs
from algorithms import volume_tracings_calculations as tracings
from ast import literal_eval

def sortFrameVolumes(method, inputFolder, sweeps):
  root, df = loader.dataModules()
  all_volumes={}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolder) # frames path
  
  for i in range(len(df)): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video
    
    if os.path.exists(FRAMES_PATH):
      try:
        volumes, *_ = funcs.calculateVolume(FRAMES_PATH, 20, sweeps, method)
        if videoName not in all_volumes and volumes is not "":
          all_volumes[videoName] = {}
          for r in range(-sweeps, sweeps+1, 1):
            all_volumes[videoName][r] = []
        
        for r in range(-sweeps, sweeps+1, 1):
          all_volumes[videoName][r].append(volumes[r])
      except:
        print(OUTPUT_FRAME_NAME)

  return all_volumes

def sortFrameVolumesFromTracings(method):
  _, _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  for i in range(len(df)):
    videoName = df.iloc[i, 0]
    
    x1 = list(literal_eval(df.iloc[i, 2])) # x1 coords
    y1 = list(literal_eval(df.iloc[i, 3])) # y1 coords
    x2 = list(literal_eval(df.iloc[i, 4])) # x2 coords
    y2 = list(literal_eval(df.iloc[i, 5])) # y2 coords
    
    number = len(x1) - 1

    maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(x1, y1, x2, y2)

    if number < 22:
      if method == "Method of Disks":
        ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Prolate Ellipsoid":
        ground_truth_volume = funcs.volumeProlateEllipsoidMethod(maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Bullet Method":
        ground_truth_volume = funcs.volumeBulletMethod(maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints)

      if videoName not in calculatedVolumeFromGroundTruth:
        calculatedVolumeFromGroundTruth[videoName] = []
      
      calculatedVolumeFromGroundTruth[videoName].append(ground_truth_volume)
  return calculatedVolumeFromGroundTruth

def sortVolumesFromFileList(root=config.CONFIG.DATA_DIR):
  givenTrueDict={}

  df = pd.read_csv(os.path.join(root, "FileList.csv"), ) # reading in FileList.csv

  for i in range(len(df)):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

def compareVolumePlot(inputFolder, method, volumeType, fromFile, sweeps, root=config.CONFIG.DATA_DIR):
  all_volumes = sortFrameVolumes(method, inputFolder, sweeps)

  if fromFile is "VolumeTracings":
    tracings_volumes = sortFrameVolumesFromTracings(method)
  else:
    tracings_volumes = sortVolumesFromFileList()

  changesInVolumesDict = {}
  for r in range(-sweeps, sweeps+1, 1):
    changesInVolumesDict[r] = []

  for videoName in tracings_volumes:
    volumeData = tracings_volumes[videoName]

    ground_truth_ESV = min(volumeData)
    ground_truth_EDV = max(volumeData)

    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100

    if videoName in all_volumes:
      for r in range(-sweeps, sweeps+1, 1):
        volumes = all_volumes[videoName][r]

        EDV = max(volumes)
        ESV = min(volumes)
        
        EF = (1 - (ESV/EDV)) * 100

        diff_EF = EF-ground_truth_EF

        diff_EDV = ((EDV-ground_truth_EDV)/ground_truth_EDV) * 100
        diff_ESV = ((ESV-ground_truth_ESV)/ground_truth_ESV) * 100
      
        if volumeType is "EF":
          changesInVolumesDict[r].append(diff_EF)
        elif volumeType is "ESV":
          changesInVolumesDict[r].append(diff_ESV)
        elif volumeType is "EDV":
          changesInVolumesDict[r].append(diff_EDV)

  return changesInVolumesDict

def createBoxPlot(inputFolder="Masks_From_VolumeTracing", method="Method of Disks", volumeType="EF",
                  fromFile="FileList", sweeps=30):
  differenceInVolumes = compareVolumePlot(inputFolder, method, volumeType, fromFile, sweeps)
  labels = []

  for i in differenceInVolumes.keys():
    labels.append(i)

  # figure related code
  loader.latexify()
  fig = plt.figure()
  fig.suptitle('Comparison', fontsize=14, fontweight='bold')
  
  _, data = differenceInVolumes.keys(), differenceInVolumes.values()

  ax = fig.add_subplot(111)
  ax.boxplot(data, showfliers=False)

  ax.set_title('Difference in Calculated ' + volumeType + ' against ' + fromFile)
  ax.set_xlabel('Angle Point Shifts')

  if volumeType is "ESV" or volumeType is "EDV":
    ax.set_ylabel('% Difference in ' + volumeType)
  else:
    ax.set_ylabel('Difference in ' + volumeType)

  ax.set_xticklabels(labels)

  # show plot
  plt.show()

#createBoxPlot(method="Method of Disks", volumeType="EF", inputFolder="Masks_From_VolumeTracing", fromFile="FileList")
#createBoxPlot(method="Method of Disks", volumeType="EF", inputFolder="Masks_From_VolumeTracing", fromFile="VolumeTracings")
#createBoxPlot(method="Method of Disks", volumeType="ESV", inputFolder="Masks_From_VolumeTracing", fromFile="VolumeTracings")
#createBoxPlot(method="Method of Disks", volumeType="EDV", inputFolder="Masks_From_VolumeTracing", fromFile="VolumeTracings")