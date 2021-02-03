"""Echonet Function Evaluation comparisons of different
methods' volume calculations against ground truth"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
import os
import config
import loader
from algorithms import funcs as funcs
from algorithms import volume_tracings_calculations as tracings
import tqdm

def sortVolumesFromAlgo(frames_path, method):

  root, df = loader.dataModules()
  all_volumes={}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, frames_path) # frames path
  
  print("Calculating volumes using algorithm")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video

    if os.path.exists(FRAMES_PATH):
      try:
        volumes, *_ = funcs.calculateVolume(FRAMES_PATH, 20, 1, method)

        if videoName not in all_volumes and volumes is not "":
          all_volumes[videoName] = []

        all_volumes[videoName].append(volumes[0])
      except:
        print(OUTPUT_FRAME_NAME)
  
  return all_volumes

def sortFrameVolumeTracings(method):
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  print("Calculating Ground Truth Values from VolumeTracings")
  for i in tqdm(range(len(df))):
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

  print("Calculating Ground Truth Values")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

def compareVolumePlot(root=config.CONFIG.DATA_DIR, pathToFrames="frames", method="Method of Disks", volumeType="ESV", fromFile=None):
  
  all_volumes = sortVolumesFromAlgo(pathToFrames, method)

  x, y = [], []
  
  if fromFile is "VolumeTracings":
    tracings_volumes = sortFrameVolumeTracings(method)
  else:
    tracings_volumes = sortVolumesFromFileList()

  for videoName in tracings_volumes:
    volumeData = tracings_volumes[videoName]

    ground_truth_ESV = min(volumeData)
    ground_truth_EDV = max(volumeData)
    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100

    if videoName in all_volumes:
      volumes = all_volumes[videoName]
      
      if len(volumes) > 1:
        EDV = max(volumes)
        ESV = min(volumes)
        EF = (1 - (ESV/EDV)) * 100
        
        if abs(EF - ground_truth_EF) > 10:
          print([videoName])
        if volumeType is "EF":
          x.append(EF)
          y.append(ground_truth_EF)
        elif volumeType is "ESV":
          x.append(EF)
          y.append(ground_truth_EF)

        elif volumeType is "EDV":
          x.append(EF)
          y.append(ground_truth_EF)

  loader.latexify()
  title = "Algorithm " + volumeType + " vs. Ground Truth " + volumeType
  xlabel = "Algorithm " + volumeType
  ylabel = 'Ground Truth ' + volumeType
  loader.scatterPlot(title=title, xlabel=xlabel, ylabel=ylabel, x1=x, y1=y, lineOfBestFit=True)

compareVolumePlot(method="Method of Disks", volumeType="EF", fromFile="FileList", pathToFrames="Masks_From_VolumeTracing")