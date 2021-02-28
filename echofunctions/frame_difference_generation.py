"""Outputting frames with differences in true ESV frame index"""

import pandas as pd
from ast import literal_eval
import os
import cv2
import loader
import time
import operator
from algorithms import funcs
from algorithms import volume_tracings_calculations as tracings
import glob
from tqdm import tqdm

def createOutputFrames(inputFolderName, outputFolderName, method):
  """Function to extract frames from input video file
  and save them as separate frames in an output directory.
  Args:
      videoName: Input video name.
      outputFolderName: Output directory to save the frames.
  Returns:
      None
  """

  failed_videos = 0
  
  df = pd.read_csv(os.path.join(root, "Frame Timing Predictions.csv")) # reading in CSV

  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 1] # name of video
    ESV_frame = df.iloc[i, 2] # ESV timing

    inputVideoPath = os.path.join(root, inputFolderName, videoName + ".avi")
    outputPath = os.path.join(root, outputFolderName)
    currentVideoPath = os.path.join(outputPath, videoName)

    os.makedirs(outputPath, exist_ok=True) # creates parent directory for storing frames
    os.makedirs(currentVideoPath, exist_ok=True) # creates folder for each video under parent directory
    
    if ESV_frame < 16:
      clipNumber, clipEnd = 0, ESV_frame + 15 # clip start, clip end
      outputFrameName = -ESV_frame
    else:
      clipNumber, clipEnd = ESV_frame - 15, ESV_frame + 15 # clip start, clip end
      outputFrameName = -15

    try:
      cap = cv2.VideoCapture(inputVideoPath)
      cap.set(clipNumber, clipEnd)
      
      while cap.isOpened():
        ret, frame = cap.read()
        
        # Crop
        x1, y1, x2, y2 = 0, 0, 112, 112 # cropping coords and specs
        crop = frame[x1:x2, y1:y2]
        
        cv2.imwrite(os.path.join(currentVideoPath, str((outputFrameName)) + ".jpg"), crop)
        clipNumber += 1
        outputFrameName += 1
        if (clipNumber is clipEnd):
          cap.release()
          break
    except:
      failed_videos += 1


createOutputFrames("segmented-videos", "find_peaks", "Method of Disks")