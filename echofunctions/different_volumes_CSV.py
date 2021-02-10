"""Creating output CSV data for different 
volume calculations for a video"""

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

# Returns dictionary with truth values from FileList.csv
def sortVolumesFromFileList(root=config.CONFIG.DATA_DIR):
  trueVolumesDict={}

  df = pd.read_csv(os.path.join(root, "FileList.csv")) # reading in FileList.csv

  print("Gathering volumes from FileList")
  for i in tqdm(range(len(df))): # iterate through each video in FileList.csv
    videoName = df.iloc[i, 0] # video name from FileList
    ground_truth_ESV = df.iloc[i, 2] # true ESV value
    ground_truth_EDV = df.iloc[i, 3] # true EDV value
    
    trueVolumesDict[videoName] = [ground_truth_ESV, ground_truth_EDV] # video name (key), volumes (values)

  return trueVolumesDict

# Return dictionary of volume data calculated from coordinates given in VolumeTracings
def sortFrameVolumesFromTracings(method):
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

# Returns dictionary of calculated volumes from algorithm
def calculateVolumesWithAlgorithm(method, inputFolderPath, task):
  root, df = loader.dataModules()
  calculatedData, failed_calculation = {}, 0

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderPath) # frames path
  
  print("\nCalculating volumes for both frames for each given video")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    if (i % 2) is 0:
      videoName = df.iloc[i, 0] + ".avi" # name of video
      frameNumber = df.iloc[i, 1] # timing for clip
      
      # Finds EDV
      frameIndices = df[df['FileName']==df.iloc[i, 0]]['Frame'].values
      frameIndices = [int(i) for i in frameIndices]

      x1 = df[df['FileName']==df.iloc[i, 0]]['X1'].values
      x2 = df[df['FileName']==df.iloc[i, 0]]['X2'].values
      y1 = df[df['FileName']==df.iloc[i, 0]]['Y1'].values
      y2 = df[df['FileName']==df.iloc[i, 0]]['Y2'].values

      volumesDict = {}
      for i in [0, 1]:
        number = 20
        frameNumber = frameIndices[i]

        maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(list(literal_eval(x1[i])), list(literal_eval(y1[i])), list(literal_eval(x2[i])), list(literal_eval(y2[i])))
        ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
        
        volumesDict[frameNumber] = ground_truth_volume

      ES = min(volumesDict.items(), key=operator.itemgetter(1))[0]
      ED = max(volumesDict.items(), key=operator.itemgetter(1))[0]

      ES_FRAME_FILENAME = videoName + "_" + str(ES) + ".png" # concatenate video name with frame number as file name
      ED_FRAME_FILENAME = videoName + "_" + str(ED) + ".png" # concatenate video name with frame number as file name

      ES_FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, ES_FRAME_FILENAME) # path to each video
      ED_FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, ED_FRAME_FILENAME) # path to each video

      if os.path.exists(ES_FRAMES_PATH):
        try:
          if task == "Erosion and Dilation":
            ES_volumes, *_ = funcs.calculateVolumeErosionAndDilation(ES_FRAMES_PATH, 20, iterations=5, method=method)
            ED_volumes, *_ = funcs.calculateVolumeErosionAndDilation(ED_FRAMES_PATH, 20, iterations=1, method=method)

          elif task == "Main Axis Top Shift":
            ES_volumes, x1s, y1s, x2s, y2s = funcs.calculateVolumeMainAxisTopShift(ES_FRAMES_PATH, 20, pointShifts=15, method=method)
            ED_volumes = funcs.calculateVolumeMainAxisTopShift(ED_FRAMES_PATH, 20, pointShifts=1, method=method)
            
          elif task == "Main Axis Bottom Shift":
            ES_volumes, x1s, y1s, x2s, y2s = funcs.calculateVolumeMainAxisBottomShift(ES_FRAMES_PATH, 20, pointShifts=15, method=method)
            ED_volumes, x1s, y1s, x2s, y2s = funcs.calculateVolumeMainAxisBottomShift(ED_FRAMES_PATH, 20, pointShifts=1, method=method)
          
          elif task == "Angle Shift":
            volumes, x1s, y1s, x2s, y2s, degrees = funcs.calculateVolumeAngleShift(ES_FRAMES_PATH, 20, sweeps=10, method=method)
          
          for shift in ES_volumes: # each shift (key) in volumes
            if videoName not in calculatedData: # create sub-dictionary if video name not in dictionary
              calculatedData[videoName] = {}

            if shift not in calculatedData[videoName]: # create array if shift not in sub-dictionary 
              calculatedData[videoName][shift] = []

            if task == "Angle Shift":
              calculatedData[videoName][shift].append([volumes[shift], degrees[shift]]) # add volumes for each shift and degrees for angle change
            else:
              calculatedData[videoName][shift] = [ES_volumes[shift], ED_volumes[0]] # add volumes for each shift
        except:
          failed_calculation += 1 # if exception case, add 1 (each frame unable to be calculated)

  print(str(failed_calculation) + " were not able to be calculated") # total number of exception frames
  
  return calculatedData

# Compare volumes from FileList against calculations
def compareVolumePlot(method="Method of Disks", inputFolderPath=None, fileName="angleSweeps.csv",
                      task="Erosion and Dilation", fromFile="VolumeTracings"):
  
  calculatedData = calculateVolumesWithAlgorithm(method, inputFolderPath, task) # dictionary of all different coords

  if fromFile == "FileList":
    trueData = sortVolumesFromFileList() # given volume data from FileList
  else:
    trueData = sortFrameVolumesFromTracings(method) # given volume data from FileList
  
  dataList = []
  for videoName in calculatedData:
    if videoName in trueData:
      volumes = calculatedData[videoName] # calculated volumes for given video
      groundtrue_ESV = min(trueData[videoName]) # true ESV from FileList
      groundtrue_EDV = max(trueData[videoName]) # true EDV from FileList
      groundtrue_EF = (1 - (groundtrue_ESV/groundtrue_EDV))*100 # true EF from FileList
    
    for shift in volumes: # iterate through each shift (key in dictionary)
      ESV = volumes[shift][0] # calculated ESV
      EDV = volumes[shift][1] # calculated EDV

      EF = (1 - (ESV/EDV)) * 100 # calculated EF

      if task == "Erosion and Dilation":
        miniDict = {'Video Name': videoName, "Percent Change": shift, "Calculated EF": EF, "Calculated ESV": ESV,
                    "Calculated EDV": EDV, "True EF": groundtrue_EF, "True ESV": groundtrue_ESV, "True EDV": groundtrue_EDV}
      
      elif task == "Main Axis Top Shift" or "Main Axis Bottom Shift":
        miniDict = {'Video Name': videoName, "Point Shift": int(shift * 100), "Calculated EF": EF, "Calculated ESV": ESV,
                    "Calculated EDV": EDV, "True EF": groundtrue_EF, "True ESV": groundtrue_ESV, "True EDV": groundtrue_EDV}
      
      elif task == "Angle Shift": # add degrees of angle change to dictionary
        esvAngleShiftIndex = [volumes[shift][i][0] for i in range(len(volumes[shift]))].index(ESV) # index of ESV angle
        edvAngleShiftIndex = [volumes[shift][i][0] for i in range(len(volumes[shift]))].index(EDV) # index of EDV angle
        
        esvAngleShift = volumes[shift][esvAngleShiftIndex][1] # angle for ESV
        edvAngleShift = volumes[shift][edvAngleShiftIndex][1] # angle for EDV

        efAngleShift = (edvAngleShift + esvAngleShift)/2 # EF angle shift is average of ESV and EDV angle shift

        miniDict = {'Video Name': videoName, "Sweep": shift, 'ESV Angle Shift': esvAngleShift,
                    "EDV Angle Shift": edvAngleShift, "EF Angle Shift": efAngleShift, "Calculated EF": EF, "Calculated ESV": ESV,
                    "Calculated EDV": EDV, "True EF": groundtrue_EF, "True ESV": groundtrue_ESV, "True EDV": groundtrue_EDV}
      
      dataList.append(miniDict) # add the sub-dictionaries (each video)
      
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(config.CONFIG.DATA_DIR, fileName) # path to export

  df.to_csv(export_path) # export to CSV

compareVolumePlot(method="Method of Disks", inputFolderPath="frames", fileName="Erosion and Dilation.csv",
                  task="Erosion and Dilation", fromFile="VolumeTracings")