"""Creates ES and ED frames from given paths."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
import os
import config
import loader
import cv2
from tqdm import tqdm

def exportFrames():
  root, _ = loader.dataModules()
  df = pd.read_csv(os.path.join(root, "Frame Predictions.csv")) # reading in CSV

  count = 0
  total_vids = 0
  
  print("Exporting frames")
  for i in tqdm(range(len(df))):
    total_vids+=1
    try:
      videoName = df.iloc[i, 1]
      ESV_frame = int(df.iloc[i, 4])
      EDV_frame = int(df.iloc[i, 5])

      videoPath = os.path.join(root, "Videos-Segmented", videoName)
      ESV_crop = loader.READ_AND_CROP_FRAME(videoPath, ESV_frame)
      EDV_crop = loader.READ_AND_CROP_FRAME(videoPath, EDV_frame)
      
      cv2.imwrite(os.path.join(root, "frames", videoName + "_" + str(ESV_frame) + ".png"), ESV_crop)
      cv2.imwrite(os.path.join(root, "frames", videoName + "_" + str(EDV_frame) + ".png"), EDV_crop)
    except:
     count+=1
  print(count)
  print(total_vids)

exportFrames()
