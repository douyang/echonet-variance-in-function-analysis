"""Echonet Function Evaluation comparisons of different methods'
 angle shifts to compare volume vs. ground truth on angle changes"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import operator
import config
import loader
from algorithms import funcs as funcs
from algorithms import volume_tracings_calculations as tracings
import collections
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
        volumes, x1, y1, x2, y2, degrees = funcs.calculateVolume(FRAMES_PATH, 20, sweeps, method)
        if videoName not in all_volumes and volumes is not "":
          all_volumes[videoName] = {}
        for r in range(-(sweeps), sweeps+1, 1):
          if r not in all_volumes[videoName]:
            all_volumes[videoName][r] = [], []
          
          all_volumes[videoName][r][0].append(volumes[r])
          all_volumes[videoName][r][1].append(degrees[r])
      except:
        print(OUTPUT_FRAME_NAME)

  return all_volumes

def sortFrameVolumesFromTracings(method):
  _, df = loader.dataModules()
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

def compareVolumePlot(inputFolder, method, volumeType, fromFile, normalized, sweeps, root=config.CONFIG.DATA_DIR):
  all_volumes = sortFrameVolumes(method, inputFolder, sweeps)

  if fromFile is "VolumeTracings":
    tracings_volumes = sortFrameVolumesFromTracings(method)
  else:
    tracings_volumes = sortVolumesFromFileList()

  changesInVolumesDict = {}

  for videoName in tracings_volumes:
    volumeData = tracings_volumes[videoName]

    ground_truth_ESV = min(volumeData)
    ground_truth_EDV = max(volumeData)
    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100

    if videoName in all_volumes:
      for angleShift in all_volumes[videoName]:
        angleChanges = all_volumes[videoName][angleShift][1]
        if len(angleChanges) > 1:
          volumes = all_volumes[videoName][angleShift][0]
          
          ZerothEDV = ((max(all_volumes[videoName][0][0]) - ground_truth_EDV)/ground_truth_EDV) * 100
          ZerothESV = ((min(all_volumes[videoName][0][0]) - ground_truth_ESV)/ground_truth_ESV) * 100

          angleChangeAverage = (angleChanges[0] + angleChanges[1])/2

          EDV = max(volumes)
          ESV = min(volumes)

          EDV_anglechange = angleChanges[volumes.index(max(volumes))]
          ESV_anglechange = angleChanges[volumes.index(min(volumes))]
          
          EF = (1 - (ESV/EDV)) * 100
          diff_EF = (EF-ground_truth_EF)

          if normalized:
            diff_EDV = (((EDV-ground_truth_EDV)/ground_truth_EDV) * 100) - ZerothEDV
            diff_ESV = (((ESV-ground_truth_ESV)/ground_truth_ESV) * 100) - ZerothESV
          else:
            diff_EDV = ((EDV-ground_truth_EDV)/ground_truth_EDV) * 100
            diff_ESV = ((ESV-ground_truth_ESV)/ground_truth_ESV) * 100

          if volumeType is "EF":
            if int(angleChangeAverage) not in changesInVolumesDict:
              changesInVolumesDict[int(angleChangeAverage)] = []
            
            changesInVolumesDict[int(angleChangeAverage)].append(diff_EF)
          elif volumeType is "ESV":
            if int(ESV_anglechange) not in changesInVolumesDict:
              changesInVolumesDict[int(ESV_anglechange)] = []
            
            changesInVolumesDict[int(ESV_anglechange)].append(diff_ESV)

            if diff_ESV > 20 and abs(ESV_anglechange) < 10:
              print(diff_ESV)
          elif volumeType is "EDV":
            if int(EDV_anglechange) not in changesInVolumesDict:
              changesInVolumesDict[int(EDV_anglechange)] = []
            
            changesInVolumesDict[int(EDV_anglechange)].append(diff_EDV)
            if diff_EDV > 20 and abs(EDV_anglechange) < 10:
              print(diff_EDV)
  
  return changesInVolumesDict

def createBoxPlot(inputFolder="Masks_From_VolumeTracing", method="Method of Disks", volumeType="EF",
                  fromFile="FileList", normalized=True, sweeps=30):
  changesInVolumesDict = compareVolumePlot(inputFolder, method, volumeType, fromFile, normalized, sweeps)

  differenceInVolumes = {}

  for key in changesInVolumesDict:
    if key == 0:
      bucket = (0, 0)
    else:
      residue = key % 5
      lowerBucketValue = key - residue
      lowerBucketValue = lowerBucketValue - 180 if lowerBucketValue > 90 else lowerBucketValue
      lowerBucketValue = lowerBucketValue + 180  if lowerBucketValue < -90 else lowerBucketValue

      upperBucketValue = lowerBucketValue + 5
      bucket = (int(lowerBucketValue), int(upperBucketValue))

    if bucket not in differenceInVolumes:
      differenceInVolumes[bucket] = []
    differenceInVolumes[bucket] += changesInVolumesDict[key]
  
  differenceInVolumes = list(differenceInVolumes.items())
  differenceInVolumes.sort(key=lambda volumeShift: volumeShift[0][0])

  # setting x-tick labels
  labels = [str(volumeShift[0]) for volumeShift in differenceInVolumes]
  data = [volumeShift[1] for volumeShift in differenceInVolumes]

  # figure related code
  loader.latexify()
  fig = plt.figure()
  fig.suptitle('Comparison', fontsize=14, fontweight='bold')

  ax = fig.add_subplot(111)
  ax.boxplot(data, showfliers=False)

  if not normalized:
    ax.set_title('Difference in Calculated ' + volumeType + ' against ' + fromFile)
  else:
    ax.set_title('Normalized (from mean) Difference in Calculated ' + volumeType + ' against ' + fromFile)
yth
  ax.set_xlabel('Angle Changes (Degrees)')

  if volumeType is "ESV" or volumeType is "EDV":
    ax.set_ylabel('% Difference in ' + volumeType)
  else:
    ax.set_ylabel('Difference in ' + volumeType)

  ax.set_xticklabels(labels, Rotation=45)
  
  # show plot
  plt.show()

# createBoxPlot(method="Method of Disks", volumeType="EDV", inputFolder="Masks_From_VolumeTracing", 
#               fromFile="VolumeTracings", normalized=True, sweeps=30)

# createBoxPlot(method="Method of Disks", volumeType="EDV", inputFolder="Masks_From_VolumeTracing", 
#               fromFile="VolumeTracings", normalized=False, sweeps=30)

# createBoxPlot(method="Method of Disks", volumeType="ESV", inputFolder="Masks_From_VolumeTracing", 
#               fromFile="VolumeTracings", normalized=True, sweeps=30)

# createBoxPlot(method="Method of Disks", volumeType="ESV", inputFolder="Masks_From_VolumeTracing", 
#               fromFile="VolumeTracings", normalized=False, sweeps=30)
