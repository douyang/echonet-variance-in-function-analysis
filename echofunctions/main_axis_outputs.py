"""Creating output CSV data on length of main axis
line for each of the frames of a given video"""

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import loader
from algorithms import funcs as funcs
import config

def calculateLength(x1, y1, x2, y2):
  """Returns a value of distance between two sets of coordinates
  """
  dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

  return dist

# Capture and Make Frames + Crop
def sortCoords(method, inputFolderPath):

  root, df = loader.dataModules() #Tracings CSV
  calculatedData = {}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderPath) # frames path
  
  for i in range(len(df)): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    FRAME_FILENAME = videoName + ".avi_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, FRAME_FILENAME) # path to each video

    if os.path.exists(FRAMES_PATH):
      try:
        volumes, x1s, y1s, x2s, y2s, degrees = funcs.calculateVolume(FRAMES_PATH, 20, 0, method)
        
        axis_length = calculateLength(x1s[0][0], y1s[0][0], x2s[0][0], y2s[0][0]) # pass in only main axis line coords
        
        if videoName not in calculatedData:
            calculatedData[videoName] = []
        
        calculatedData[videoName].append([frameNumber, axis_length])
      except:
        print(FRAME_FILENAME)

  return calculatedData

def exportCSV(method="Method of Disks", inputFolderPath=None, fileName="axis-lengths.csv"):
    calculatedData = sortCoords(method, inputFolderPath) # dictionary of all different coords

    dataList = []
    for videoName in calculatedData:
      for i in range(1):
        miniDict = {'Video Name': videoName, "Frame Number": calculatedData[videoName][i][0], 'Main Axis Length': calculatedData[videoName][i][1]}
        dataList.append(miniDict)

    df = pd.DataFrame(dataList)

    export_path = os.path.join(config.CONFIG.DATA_DIR, fileName)

    df.to_csv(export_path, index=False)

exportCSV(method="Method of Disks", inputFolderPath="Masks_From_VolumeTracing", fileName="axis_lengths.csv")