"""CSV with volumes with frames off from true ESV"""

import pandas as pd
from ast import literal_eval
import os
import cv2
import loader
import config
import time
import operator
from algorithms import funcs
from algorithms import volume_tracings_calculations as tracings
import glob
from tqdm import tqdm

def exportTimingsCSV(inputFolderName="ESV_sweeps",
                            fileName="Frame Differences from EDV Timing.csv"):
  
  root, _ = loader.dataModules()
  ESV_path = os.path.join(root, inputFolderName)
  
  dataList, exception_files = [], 0

  df = pd.read_csv(os.path.join(root, "Frame Timing Predictions.csv")) # reading in CSV

  for i in tqdm(range(len(df))): # iterates through each row of data frame
    frameNumber = -16
    videoName = os.path.splitext(df.iloc[i, 1])[0] # name of video
    ESV_frame = df.iloc[i, 2] # ESV timing

    videoDict = {"Video Name": videoName}
    
    folder_path = os.path.join(ESV_path, videoName)

    if ESV_frame < 15:
      frameDeviationStart, frameDeviationEnd = 0, ESV_frame + 15 # frame start, frame end

    else:
      frameDeviationStart, frameDeviationEnd = ESV_frame - 15, ESV_frame + 15 # clip start, clip end

    for frame in range(frameDeviationStart, frameDeviationEnd):
      frameNumber += 1
      frame_path = os.path.join(folder_path, str(frame) + ".jpg")
      frameVolumes = {}

      try:
        volumes, x1, y1, x2, y2 = funcs.calculateVolumeErosionAndDilation(frame_path, 20, iterations=1, method="Method of Disks")
        frameVolumes[frameNumber] = volumes[0]
        
        frameVolumes = {key:value for key, value in sorted(frameVolumes.items(), key=lambda item: int(item[0]))} # sorting numerically
        videoDict.update(frameVolumes)
        
      except:
        exception_files += 1
        print(videoName, frame)

    dataList.append(videoDict)
  
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(root, fileName) # path to export

  df.to_csv(export_path) # export to CSV

exportTimingsCSV(inputFolderName="find_peaks", fileName="Frame Differences from EDV Timing.csv")