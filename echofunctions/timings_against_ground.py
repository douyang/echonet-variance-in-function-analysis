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

def sortVolumesFromAlgo(frames_path, method):

  root, df = loader.dataModules()
  all_volumes={}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, frames_path) # frames path
  
  for i in range(len(df)): # iterates through each row of data frame
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

  _, tracings = loader.dataModules()
  imageLines = {}
  
  for i in range(len(tracings)):
    videoName = tracings.iloc[i, 0]
    x1 = list(literal_eval(tracings.iloc[i, 2])) # x1 coords
    
    number = len(x1)

    imageLines[videoName] = number

  for i in range(len(df)):
    videoName = df.iloc[i, 0]
    if videoName in imageLines and imageLines[videoName] < 22:
      ground_truth_ESV = df.iloc[i, 2]
      ground_truth_EDV = df.iloc[i, 3]

      if videoName not in givenTrueDict:
        givenTrueDict[videoName] = []
      
      givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

def compareVolumePlot(root=config.CONFIG.DATA_DIR, pathToFrames="frames", method="Method of Disks", volumeType="ESV", fromFile=None):
  
  all_volumes = sortVolumesFromAlgo(pathToFrames, method)

  x, y = [], []
  badMasks = ['0X12430512E2BBCD55.avi', '0X208FBB50F39AAF69.avi', '0X222D850B21C1CBBF.avi', '0X2507255D8DC30B4E.avi', '0X280B7441A7E287B2.avi', '0X28980B95F9769CE7.avi', '0X3269691452F4F42A.avi', '0X35A5E9C9075E56EE.avi', '0X366AD377E4A81FBE.avi', '0X367085DDC2E90657.avi', '0X3A79044052AC3197.avi', '0X42186EEA400ABD80.avi', '0X4477077E68BF47B2.avi', '0X46ACC9C2CF9CFB1E.avi', '0X49620F7B3E4CA28A.avi', '0X4B3A70F6BD40224B.avi', '0X4E4FDDC1BB14AC83.avi', '0X4E9F08061D109568.avi', '0X53BD50EB0C43D30D.avi', '0X56BAEFC36506EC74.avi', '0X56FC2793F196F52C.avi', '0X580E9EB1627EA2EC.avi', '0X59D1140D8320A782.avi', '0X59D5F41F45601E03.avi', '0X5D38D994C2490EAE.avi', '0X642E639A8CDE539B.avi', '0X66CE85713FABD830.avi', '0X6C124671AA84BFE1.avi', '0X6E02E0F24F63EFD7.avi', '0X75ED030E56E85A27.avi', '0X7B1F112049D754D9.avi']
  
  if fromFile is "VolumeTracings":
    tracings_volumes = sortFrameVolumeTracings(method)
  else:
    tracings_volumes = sortVolumesFromFileList()

  for videoName in tracings_volumes:
    volumeData = tracings_volumes[videoName]


    ground_truth_ESV = min(volumeData)
    ground_truth_EDV = max(volumeData)
    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100

    if videoName in all_volumes and videoName not in badMasks:
      volumes = all_volumes[videoName]
      
      if len(volumes) > 1:
        EDV = max(volumes)
        ESV = min(volumes)
        EF = (1 - (ESV/EDV)) * 100
        
        if abs(EF - ground_truth_EF) > 8:
          print([videoName], imageLines[videoName])

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