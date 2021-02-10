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

def compareEjectionFraction(inputFolderName="ESV_sweeps", outputFolderName="ESV frame modulation",
                            fileName="Frame Differences from EDV Timing.csv"):
  
  root, df = loader.dataModules()
  ESV_path = os.path.join(root, inputFolderName)
  
  dataList, exception_files = [], 0

  for video in tqdm(os.listdir(ESV_path)):
    videoDict = {"Video Name": video}
    try:
      frameVolumes = {}
      for frame in os.listdir(os.path.join(ESV_path, video)):
        frame_path = os.path.join(ESV_path, video, frame)

        frameNumber = os.path.basename(frame_path).split("_")[1].split(".")[0]
        
        volumes, x1, y1, x2, y2 = funcs.calculateVolumeErosionAndDilation(frame_path, 20, iterations=1, method="Method of Disks")
        frameVolumes[frameNumber] = volumes[0]
      
      frameVolumes = {key:value for key, value in sorted(frameVolumes.items(), key=lambda item: int(item[0]))} # sorting numerically
      videoDict.update(frameVolumes)
      
      dataList.append(videoDict)
    except:
      exception_files += 1
  
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(root, fileName) # path to export

  df.to_csv(export_path) # export to CSV
  print(exception_files)

compareEjectionFraction(inputFolderName="ESV_sweeps", outputFolderName="ESV frame modulation",
                        fileName="Frame Differences from EDV Timing.csv")