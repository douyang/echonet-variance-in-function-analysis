"""Echonet Function Evaluation comparisons of different
methods to calculate the volume against each other"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
import os
import mask
import config
import loader
from algorithms import funcs
import tqdm

# Capture and Make Frames + Crop
def sortFrameVolumes1(method):

  root, df = loader.dataModules()
  all_volumes={}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, "frames") # frames path
  
  print("Calculating volumes using second method..")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video
    
    numberOfParallelLines = len(literal_eval(df.iloc[i, 2])) - 1 # number of parallel lines for each mask

    volumes, *_ = funcs.calculateVolume(FRAMES_PATH, numberOfParallelLines, method)

    if videoName not in all_volumes and volumes is not "":
        all_volumes[videoName] = []

    try:
      all_volumes[videoName].append(volumes[0])
    except:
      continue
  
  return all_volumes

def sortFrameVolumes2(method):

  root, df = loader.dataModules()
  all_volumes={}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, "frames") # frames path
  
  print("Calculating volumes using second method..")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video
    
    numberOfParallelLines = len(literal_eval(df.iloc[i, 2])) - 1 # number of parallel lines for each mask

    volumes, *_ = funcs.calculateVolume(FRAMES_PATH, numberOfParallelLines, method)

    if videoName not in all_volumes and volumes is not "":
      all_volumes[videoName] = []

    if volumes is not "":
      all_volumes[videoName].append(volumes[0])
  
  return all_volumes

def compareVolumePlot(root=config.CONFIG.DATA_DIR, method1="Method of Disks", method2="Prolate Ellipsoid", timing="EF"):
    x, y = [], []

    df = pd.read_csv(os.path.join(root, "FileList.csv")) # read in FileList.csv
    volumes1 = sortFrameVolumes1(method=method1) # dictionary of all volumes1
    volumes2 = sortFrameVolumes2(method=method2) # dictionary of all volumes2

    print("Comparing volumes and generating plot")
    for i in tqdm(range(len(df))):
      videoName = df.iloc[i, 0]

      if (videoName in volumes1) and (videoName in volumes2):
        EDV1 = max(volumes1[videoName])
        ESV1 = min(volumes1[videoName])

        EDV2 = max(volumes2[videoName])
        ESV2 = min(volumes2[videoName])

        EF1 = (1 - (ESV1/EDV1)) * 100
        EF2 = (1 - (ESV2/EDV2)) * 100

        if timing is "EDV":
          x.append(EDV1)
          y.append(EDV2)

        elif timing is "ESV":
          x.append(ESV1)
          y.append(ESV2)

        elif timing is "EF":
          x.append(EF1)
          y.append(EF2)

    title = method1 + ' ' + timing + ' vs. ' + method2 + ' ' + timing
    xlabel = method1 + ' Calculated ' + timing
    ylabel = method2 + ' Calculated ' + timing
    loader.scatterPlot(title=title, xlabel=xlabel, ylabel=ylabel, x1=x, y1=y, lineOfBestFit=False)

compareVolumePlot(method1="Bullet", method2="Prolate Ellipsoid", timing="EDV")