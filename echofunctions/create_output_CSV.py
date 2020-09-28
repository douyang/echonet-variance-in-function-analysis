"""Creating output CSV data on mask coordinates
and different volume calculations for a video"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import loader
from algorithms import funcs as funcs
import config

# Capture and Make Frames + Crop
def sortCoords(method, inputFolderPath):

  root, df = loader.dataModules()
  calculatedData = {}

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderPath) # frames path
  
  for i in range(len(df)): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    FRAME_FILENAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, FRAME_FILENAME) # path to each video

    if os.path.exists(FRAMES_PATH):
      try:
        volumes, *_ = funcs.calculateVolume(FRAMES_PATH, 20, method)
        
        for angleShift in volumes:
          if videoName not in calculatedData:
            calculatedData[videoName] = {}

          if angleShift not in calculatedData[videoName]:
            calculatedData[videoName][angleShift] = []
        
          calculatedData[videoName][angleShift].append(volumes[angleShift])
      except:
        print(FRAME_FILENAME)
  return calculatedData

def compareVolumePlot(method="Method of Disks", inputFolderPath=None):
    calculatedData = sortCoords(method, inputFolderPath) # dictionary of all different coords
    
    video, ef, esv, edv = [], [], [], []
    for videoName in calculatedData:
      volumes = calculatedData[videoName]

      for angleShift in volumes:
        EDV = max(volumes[angleShift])
        ESV = min(volumes[angleShift])
        EF = (1 - (ESV/EDV)) * 100

        video.append(video)
        ef.append(EF)
        esv.append(esv)
        edv.append(edv)
        
    
    d = {'Video Name': video,'EF': ef, "ESV": esv, "EDV": edv}
    df = pd.DataFrame(d)
    #df.set_index('Video Name', inplace=True)
    
    export_path = os.path.join(config.CONFIG.DATA_DIR, method + "-Volume.csv")

    df.to_csv(export_path)

compareVolumePlot(method="Method of Disks", inputFolderPath="Masks_From_VolumeTracing")