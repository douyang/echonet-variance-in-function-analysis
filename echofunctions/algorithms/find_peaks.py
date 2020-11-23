"""Finding the ES and ED frames based on
max and min volume calculations, respectively"""

import pandas as pd
from ast import literal_eval
import os
import cv2
import loader
import time
import operator
from algorithms import funcs

def calculateVolumesForEachFrame(videoName, outputFolderName, method):
    """Function to extract frames from input video file
    and save them as separate frames in an output directory.
    Args:
        videoName: Input video name.
        outputFolderName: Output directory to save the frames.
    Returns:
        None
    """

    root, _ = loader.dataModules()
    volumeDict = {}

    inputVideoPath = os.path.join(root, "segmented-videos", videoName)
    outputPath = os.path.join(root, outputFolderName)
    os.makedirs(outputPath, exist_ok=True) # creates folder for frames of given video
    
    cap = cv2.VideoCapture(inputVideoPath)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        # Crop
        x1, y1, x2, y2 = 0, 0, 112, 112 # cropping coords and specs
        crop = frame[x1:x2, y1:y2]

        cv2.imwrite(os.path.join(outputPath, str((count+1)) + ".jpg"), crop)
        count += 1
        if (count > (video_length-1)):
            cap.release()
            break
    
    # Calculate Volumes
    for frame in os.listdir(outputPath):
      framePath = os.path.join(outputPath, frame)
      volumes, *_ = funcs.calculateVolume(framePath, 20, 0, method)
      volumeDict[framePath] = volumes[0]
    
    return volumeDict

def returnPeaks(videoName="0X1BDEEC24D5FC570C.avi", outputFolderName="find_peaks", method="Method of Disks"):
  volumeDict = calculateVolumesForEachFrame(videoName, outputFolderName, method)
  
  v=list(volumeDict.values())
  k=list(volumeDict.keys())

  ED_index = k[v.index(max(v))]
  ES_index = k[v.index(min(v))]

  return int(os.path.splitext(os.path.basename(ES_index))[0]), int(os.path.splitext(os.path.basename(ED_index))[0])
