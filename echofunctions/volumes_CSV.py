"""Export a CSV with volume data (ESV, EDV, EF)"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import loader
from algorithms import funcs as funcs
import config
from algorithms import volume_tracings_calculations as tracings
from ast import literal_eval
from tqdm import tqdm
import operator

def sortVolumesFromAlgo(frames_path, method):

  root, df = loader.dataModules()
  all_volumes={}
  exception_files = 0

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, frames_path) # frames path
  
  print("Calculating volumes from algorithms..")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] + ".avi" # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video

    if os.path.exists(FRAMES_PATH):
      try:
        volumes, *_ = funcs.calculateVolumeMainAxisTopShift(FRAMES_PATH, 20, 1, method)

        if videoName not in all_volumes and volumes is not "":
          all_volumes[videoName] = []

        all_volumes[videoName].append(volumes[0])
      except:
        exception_files += 1
  
  return all_volumes

def sortFrameVolumeTracings(method):
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  print("\nCalculating volumes from VolumeTracings coordinates")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0] + ".avi"
    
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

  print("\nGathering volumes from FileList")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

def exportCSV(root=config.CONFIG.DATA_DIR, pathToFrames="frames", method="Method of Disks", fromFile="VolumeTracings"):
  
  all_volumes = sortVolumesFromAlgo(pathToFrames, method)

  dataList = []
  
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
        
        if EF != 0 and ground_truth_EF != 0 and abs((EF - ground_truth_EF)) < 5:
          calculatedData = {"Video Name": videoName, "Split": split, "EF": EF, "Human Tracings EF": EF,
                            "Human Tracings ESV": ESV, "Human Tracings EDV": EDV}
          dataList.append(calculatedData)
  
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(root, "Standard Volume Data.csv") # path to export

  df.to_csv(export_path) # export to CSV

exportCSV()