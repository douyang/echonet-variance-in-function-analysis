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

def exportFrames(segmentedVideosFolder="Videos-Segmented", outputFolder="red_frames"):
  """Function to create outputs of appropriate frames from a given folder of segmented videos
  Args:
      segmentedVideosFolder (str): Folder containing the segmented videos
  Returns:
      None
  """

  root, _ = loader.dataModules()
  df = pd.read_csv(os.path.join(root, "Frame Predictions.csv")) # reading in CSV
  
  print("\nExporting frames")
  for i in tqdm(range(len(df))):
    try:
      videoName = df.iloc[i, 1]
      ESV_frame = int(df.iloc[i, 4])
      EDV_frame = int(df.iloc[i, 5])

      videoPath = os.path.join(root, segmentedVideosFolder, videoName)

      ESV_crop = loader.READ_AND_CROP_FRAME(videoPath, ESV_frame) # crop of ESV frame
      EDV_crop = loader.READ_AND_CROP_FRAME(videoPath, EDV_frame) # crop of EDV frame
      
      cv2.imwrite(os.path.join(root, outputFolder, videoName + "_" + str(ESV_frame) + ".png"), ESV_crop)
      cv2.imwrite(os.path.join(root, outputFolder, videoName + "_" + str(EDV_frame) + ".png"), EDV_crop)
    except:
     print("Failed to export " + videoName)
