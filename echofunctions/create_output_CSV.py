"""Creating output CSV data for different 
volume calculations for a video"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import loader
from algorithms import funcs as funcs
import config
from tqdm import tqdm

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

# Returns dictionary of calculated volumes from algorithm
def calculateVolumesWithAlgorithm(method, inputFolderPath, task):
  root, df = loader.dataModules()
  calculatedData, failed_calculation = {}, 0

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderPath) # frames path
  
  print("Calculating volumes for both frames for each given video")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] + ".avi" # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    FRAME_FILENAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, FRAME_FILENAME) # path to each video
    if os.path.exists(FRAMES_PATH):
      try:
        if task == "Erosion and Dilation":
          volumes, x1s, y1s, x2s, y2s = funcs.calculateVolumeErosionAndDilation(FRAMES_PATH, 20, iterations=5, method=method)
        
        elif task == "Main Axis Shift":
          volumes, x1s, y1s, x2s, y2s = funcs.calculateVolumeMainAxisShift(FRAMES_PATH, 20, pointShifts=15, method=method)
        
        elif task == "Angle Shift":
          volumes, x1s, y1s, x2s, y2s, degrees = funcs.calculateVolumeAngleShift(FRAMES_PATH, 20, sweeps=15, method=method)
        
        for shift in volumes: # each shift (key) in volumes
          if videoName not in calculatedData: # create sub-dictionary if video name not in dictionary
            calculatedData[videoName] = {}

          if shift not in calculatedData[videoName]: # create array if shift not in sub-dictionary 
            calculatedData[videoName][shift] = []

          if task == "Angle Shift":
            calculatedData[videoName][shift].append([volumes[shift], degrees[shift]]) # add volumes for each shift and degrees for angle change
          else:
            calculatedData[videoName][shift].append([volumes[shift]]) # add volumes for each shift
      except:
        failed_calculation += 1 # if exception case, add 1 (each frame unable to be calculated)

  print(str(failed_calculation) + " were not able to be calculated") # total number of exception frames
  
  return calculatedData

# Compare volumes from FileList against calculations
def compareVolumePlot(method="Method of Disks", inputFolderPath=None, fileName="angleSweeps.csv", task="Erosion and Dilation"):
  calculatedData = calculateVolumesWithAlgorithm(method, inputFolderPath, task) # dictionary of all different coords
  fileListData = sortVolumesFromFileList() # given volume data from FileList
  
  dataList = []
  for videoName in calculatedData:
    volumes = calculatedData[videoName] # calculated volumes for given video
    groundtrue_ESV = min(fileListData[videoName]) # true ESV from FileList
    groundtrue_EDV = max(fileListData[videoName]) # true EDV from FileList
    groundtrue_EF = (1 - (groundtrue_ESV/groundtrue_EDV))*100 # true EF from FileList
    
    for shift in volumes: # iterate through each shift (key in dictionary)
      EDV = max([volumes[shift][i][0] for i in range(len(volumes[shift]))]) # calculated EDV
      ESV = min([volumes[shift][i][0] for i in range(len(volumes[shift]))]) # calculated ESV

      EF = (1 - (ESV/EDV)) * 100 # calculated EF

      if task == "Erosion and Dilation":
        miniDict = {'Video Name': videoName, "Iteration": shift, "Calculated EF": EF, "Calculated ESV": ESV,
                    "Calculated EDV": EDV, "True EF": groundtrue_EF, "True ESV": groundtrue_ESV, "True EDV": groundtrue_EDV}
      
      elif task == "Main Axis Shift":
        miniDict = {'Video Name': videoName, "Point Shift": shift, "Calculated EF": EF, "Calculated ESV": ESV,
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

compareVolumePlot(method="Method of Disks", inputFolderPath="frames", fileName="Erosion and Dilation Volume Data.csv",
                  task="Erosion and Dilation")