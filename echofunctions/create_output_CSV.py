"""Creating output CSV data on mask coordinates
and different volume calculations for a video"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import loader
from algorithms import funcs
import config

# Capture and Make Frames + Crop
def sortCoords(method="Method of Disks"):

  root, _, df = loader.dataModules()
  x1_coords, y1_coords, x2_coords, y2_coords, vidName, frameNum=[], [], [], [], [], []

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, "frames") # frames path
  
  for i in range(len(df)): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video

    if os.path.exists(FRAMES_PATH):
      volumes, x1s, y1s, x2s, y2s, degrees = algorithms.funcs.calculateVolume(FRAMES_PATH, 20, method)

      for coord in range(len(x1s[0])):
        vidName.append(videoName)
        frameNum.append(frameNumber)
        x1_coords.append(x1s[0][coord])
        y1_coords.append(y1s[0][coord])
        x2_coords.append(x2s[0][coord])
        y2_coords.append(y2s[0][coord])
      
  return vidName, x1_coords, y1_coords, x2_coords, y2_coords, frameNum

def compareVolumePlot(method="Method of Disks"):
    videoName, x1coords, y1coords, x2coords, y2coords, frameNum = sortCoords(method=method) # dictionary of all different coords
    
    df = pd.DataFrame(list(zip(videoName, x1coords, y1coords, x2coords, y2coords, frameNum)), columns=['Video Name', "X1", "Y1", "X2", "Y2", "Frame"])
    df.set_index('Video Name', inplace=True)
    
    export_path = os.path.join(config.CONFIG.DATA_DIR, "Coords.csv")

    df.to_csv(export_path)
        
compareVolumePlot()