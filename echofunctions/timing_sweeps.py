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
import cv2
from ast import literal_eval

def sortFrameVolumeTracings():
  calculatedVolumeFromGroundTruth={}
  
  for i in range(len(df)):
    videoName = df.iloc[i, 0] + ".avi"
    frameNumber = df.iloc[i, 1] # timing for clip

    x1 = list(literal_eval(df.iloc[i, 2])) # x1 coords
    y1 = list(literal_eval(df.iloc[i, 3])) # y1 coords
    x2 = list(literal_eval(df.iloc[i, 4])) # x2 coords
    y2 = list(literal_eval(df.iloc[i, 5])) # y2 coords
    
    number = len(x1) - 1

    maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(x1, y1, x2, y2)

    if number < 22:
      ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      if videoName not in calculatedVolumeFromGroundTruth:
        calculatedVolumeFromGroundTruth[videoName] = [], []
      
      calculatedVolumeFromGroundTruth[videoName][0].append(ground_truth_volume)
      calculatedVolumeFromGroundTruth[videoName][1].append(frameNumber)
  return calculatedVolumeFromGroundTruth

root, df = loader.dataModules()
allVolumes = sortFrameVolumeTracings()

def generateFrameSweeps(timing, makeSweepFrames):
  PATH_TO_VIDEOS = os.path.join(root, "segmented-videos") # frames path
  PATH_TO_ESVSWEEPS = os.path.join(root, "ESV_sweeps")
  PATH_TO_EDVSWEEPS = os.path.join(root, "EDV_sweeps")
  
  os.makedirs(PATH_TO_ESVSWEEPS, exist_ok=True)
  os.makedirs(PATH_TO_EDVSWEEPS, exist_ok=True)

  for i in range(len(df)): # iterates through each row of data frame
    videoName = df.iloc[i, 0] + ".avi" # name of video
    videoPath = os.path.join(PATH_TO_VIDEOS, videoName) # path to each raw video

    if (videoName in allVolumes) and (makeSweepFrames) and os.path.exists(videoPath):
      os.makedirs(os.path.join(PATH_TO_ESVSWEEPS, videoName), exist_ok=True)
      os.makedirs(os.path.join(PATH_TO_EDVSWEEPS, videoName), exist_ok=True)

      volumes = allVolumes[videoName][0]
      ESVFrame = allVolumes[videoName][1][volumes.index(min(volumes))]
      EDVFrame = allVolumes[videoName][1][volumes.index(max(volumes))]

      for frameSweep in range(int(ESVFrame)-15, int(ESVFrame)+16, 1):
        try:
          FRAME_NAME =  "frame_" + str(int(frameSweep) - int(ESVFrame)) + ".png"
          sweep_path = os.path.join(PATH_TO_ESVSWEEPS, videoName, FRAME_NAME)

          frame = loader.READ_AND_CROP_FRAME(videoPath, frameSweep, makeCrop=True)
          cv2.imwrite(sweep_path, frame)
        except:
          continue

      for frameSweep in range(int(EDVFrame)-15, int(EDVFrame)+16, 1):
        try:
          FRAME_NAME =  "frame_" + str(int(frameSweep) - int(EDVFrame)) + ".png"
          sweep_path = os.path.join(PATH_TO_EDVSWEEPS, videoName, FRAME_NAME)

          frame = loader.READ_AND_CROP_FRAME(videoPath, frameSweep, makeCrop=True)
          cv2.imwrite(sweep_path, frame)
        except:
          continue
  return PATH_TO_ESVSWEEPS, PATH_TO_EDVSWEEPS, allVolumes

def calculateSweeps(timing, makeSweepFrames):
  esv_path, edv_path, tracingsVolumes = generateFrameSweeps(timing, makeSweepFrames)

  ESV_Sweeps_Volumes = {}
  EDV_Sweeps_Volumes = {}
  EF_Sweeps_Volumes = {}

  for videoName in tracingsVolumes:
    volumeData = tracingsVolumes[videoName][0]
    ground_truth_ESV = min(volumeData)
    ground_truth_EDV = max(volumeData)
    ground_truth_EF = (ground_truth_EDV - ground_truth_ESV)/ground_truth_EDV

    if (os.path.exists(os.path.join(esv_path, videoName))) and (os.path.exists(os.path.join(edv_path, videoName))):
      for frameSweep in os.listdir(os.path.join(esv_path, videoName)):
        volumes, *_ = funcs.calculateVolume(os.path.join(esv_path, videoName, frameSweep), 20, 0, "Method of Disks")
        ESV = volumes[0]

        diff_ESV = ((ESV-ground_truth_ESV)/ground_truth_ESV) * 100

        indexName = frameSweep.split('_')[1][:-4]

        if int(indexName) not in ESV_Sweeps_Volumes:
          ESV_Sweeps_Volumes[int(indexName)] = [] 

        ESV_Sweeps_Volumes[int(indexName)].append(diff_ESV)

      for frameSweep in os.listdir(os.path.join(edv_path, videoName)):
        volumes, *_ = funcs.calculateVolume(os.path.join(edv_path, videoName, frameSweep), 20, 0, "Method of Disks")

        EDV = volumes[0]

        diff_EDV = ((EDV-ground_truth_EDV)/ground_truth_EDV) * 100

        indexName = frameSweep.split('_')[1][:-4]

        if int(indexName) not in EDV_Sweeps_Volumes:
          EDV_Sweeps_Volumes[int(indexName)] = [] 

        EDV_Sweeps_Volumes[int(indexName)].append(diff_EDV)
      
      commonFrames = list(set(os.listdir(os.path.join(edv_path, videoName))) & set(os.listdir(os.path.join(esv_path, videoName))))
      
      for frameSweep in commonFrames:
        volumes, *_ = funcs.calculateVolume(os.path.join(edv_path, videoName, frameSweep), 20, 0, "Method of Disks")
        EDV = volumes[0]

        volumes, *_ = funcs.calculateVolume(os.path.join(esv_path, videoName, frameSweep), 20, 0, "Method of Disks")
        ESV = volumes[0]
        EF = (EDV - ESV)/EDV
        diff_EF = EF - ground_truth_EF
        indexName = frameSweep.split('_')[1][:-4]

        if int(indexName) not in EF_Sweeps_Volumes:
          EF_Sweeps_Volumes[int(indexName)] = [] 

        EF_Sweeps_Volumes[int(indexName)].append(diff_EF)

  esv_dict = normalizeDict(ESV_Sweeps_Volumes)
  edv_dict = normalizeDict(EDV_Sweeps_Volumes)
  ef_dict = normalizeDict(EF_Sweeps_Volumes)

  return esv_dict, edv_dict, ef_dict

def normalizeDict(changesInVolumesDict):
  zeroItems = changesInVolumesDict[0]
  zeroItems.sort()
  shift = zeroItems[len(zeroItems)//2]

  for angle in changesInVolumesDict:
      for i in range(len(changesInVolumesDict[angle])):
          changesInVolumesDict[angle][i] -= shift
  return changesInVolumesDict

def createBoxPlot(volumeType="EDV", makeSweeps=True):
  ESVVolumes, EDVVolumes, EFVolumes = calculateSweeps(volumeType, makeSweeps)
  
  if volumeType is "ESV":
    volumesDict = ESVVolumes
  elif volumeType is "EDV":
    volumesDict = EDVVolumes
  elif volumeType is "EF":
    volumesDict = EFVolumes

  volumesDict = list(volumesDict.items())
  volumesDict.sort(key=lambda volumeShift: volumeShift[0])
  
  # Calculating error and specs
  totalErr = 0
  totalItems = 0
  for sweep in volumesDict:
    if abs(sweep) == 0:
      shifts = volumesDict[sweep]
      totalErr += sum([abs(shift) for shift in sweep[1]])
      totalItems += len(sweep[1])
  
  averageError = totalErr/totalItems
  print(averageError)

  # getting figure labels and data in right format
  labels = [volumeShift[0] for volumeShift in volumesDict]
  data = [volumeShift[1] for volumeShift in volumesDict]
  
  # figure related code
  loader.latexify()
  fig = plt.figure(figsize=(12, 8))
  plt.xticks(fontsize=18)
  plt.yticks(fontsize=18)

  ax = fig.add_subplot(111)
  ax.boxplot(data, showfliers=False)
  ax.set_xticklabels(labels, Rotation=45)
  
  # show plot
  plt.savefig("./figures/paperBoxPlots/" + volumeType + ".png", bbox_inches='tight')
  plt.show()

createBoxPlot(volumeType="ESV", makeSweeps=True)
createBoxPlot(volumeType="EDV", makeSweeps=True)