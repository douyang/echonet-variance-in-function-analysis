"""Creating output CSV data on mask coordinates
and different volume calculations for a video"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import loader
from algorithms import funcs as funcs
import config
import tqdm

def sortVolumesFromFileList(root=config.CONFIG.DATA_DIR):
  givenTrueDict={}

  df = pd.read_csv(os.path.join(root, "FileList.csv")) # reading in FileList.csv

  print("Gathering volumes from FileList")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

# Capture and Make Frames + Crop
def sortCoords(method, inputFolderPath):

  root, df = loader.dataModules()
  calculatedData = {}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderPath) # frames path
  
  print("Calculating volumes for both frames for each given video")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    FRAME_FILENAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, FRAME_FILENAME) # path to each video
    if os.path.exists(FRAMES_PATH):
      try:
        volumes, x1s, y1s, x2s, y2s, degrees = funcs.calculateVolume(FRAMES_PATH, 20, 30, method)
        
        for angleShift in volumes:
          if videoName not in calculatedData:
            calculatedData[videoName] = {}

          if angleShift not in calculatedData[videoName]:
            calculatedData[videoName][angleShift] = []
        
          calculatedData[videoName][angleShift].append([volumes[angleShift], degrees[angleShift], angleShift])
      except:
        print(FRAME_FILENAME)

  return calculatedData

def compareVolumePlot(method="Method of Disks", inputFolderPath=None, fileName = "angleSweeps.csv"):
    calculatedData = sortCoords(method, inputFolderPath) # dictionary of all different coords
    fileListData = sortVolumesFromFileList()

    dataList = []
    # cond = True
    for videoName in calculatedData:
      volumes = calculatedData[videoName]
      groundtrue_ESV = min(fileListData[videoName])
      groundtrue_EDV = max(fileListData[videoName])
      groundtrue_EF = (1 - (groundtrue_ESV/groundtrue_EDV))*100
      
      for angleShift in volumes:
        EDV = max([volumes[angleShift][i][0] for i in range(len(volumes[angleShift]))])
        ESV = min([volumes[angleShift][i][0] for i in range(len(volumes[angleShift]))])

        esvAngleShiftIndex = [volumes[angleShift][i][0] for i in range(len(volumes[angleShift]))].index(ESV)
        edvAngleShiftIndex = [volumes[angleShift][i][0] for i in range(len(volumes[angleShift]))].index(EDV)
        esvAngleShift = volumes[angleShift][esvAngleShiftIndex][1]
        edvAngleShift = volumes[angleShift][edvAngleShiftIndex][1]

        efAngleShift = (edvAngleShift + esvAngleShift)/2

        pointShift = volumes[angleShift][0][2]
        EF = (1 - (ESV/EDV)) * 100

        miniDict = {'Video Name': videoName, "Point Shift": pointShift, 'ESV Angle Shift': esvAngleShift, 'EDV Angle Shift': edvAngleShift, 'EF Angle Shift': efAngleShift, 'EF': EF, "ESV": ESV, "EDV": EDV, "True EF": groundtrue_EF, "True ESV": groundtrue_ESV, "True EDV": groundtrue_EDV}

        dataList.append(miniDict)

    df = pd.DataFrame(dataList)

    export_path = os.path.join(config.CONFIG.DATA_DIR, fileName)

    df.to_csv(export_path)

compareVolumePlot(method="Method of Disks", inputFolderPath="Masks_From_VolumeTracing", fileName = "angleSweeps.csv")