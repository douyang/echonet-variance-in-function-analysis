"""Create CSV for timing data (true frame and predicted frames)"""

import pandas as pd
import os
import config
import loader
from algorithms import funcs as funcs
import collections
import cv2
from ast import literal_eval
from tqdm import tqdm
import find_peaks

# Returns dictionary with predicted frames
def gatherTimingPredictions(inputFolder, outputFolder, CSVName):
  
  root=config.CONFIG.DATA_DIR
  videoPath = os.path.join(root, inputFolder)
  
  dataList = []
  fails, video_count = 0, 0
  checkdf = pd.read_csv("/Users/ishan/Documents/Stanford/EchoData/Frame Timing Predictions.csv")

  for videoName in tqdm(os.listdir(videoPath)):
    video_count += 1
    if videoName not in checkdf["Video Name"].to_list():
      prediction_frames, true_frames = find_peaks.returnPeaks(videoName=os.path.splitext(videoName)[0],
                                        inputFolderName=inputFolder, outputFolderName=outputFolder, makeFrames=False)
      
      ES_frame, ED_frame = prediction_frames[0], prediction_frames[1] # predicted timings
      true_ES_frame, true_ED_frame = true_frames[0], true_frames[1] # true timings

      videoData = {"Video Name": videoName, "Predicted ESV": ES_frame, "Predicted EDV": ED_frame,
                  "True ESV": true_ES_frame, "True EDV": true_ED_frame}
      
      dataList.append(videoData) # add the sub-dictionaries (each video)
    
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(root, CSVName) # path to export

  df.to_csv(export_path) # export to CSV
  print(fails)
  print(video_count)
gatherTimingPredictions("Videos-Segmented", "find-peaks", "Frame Timing Predictions (1).csv")