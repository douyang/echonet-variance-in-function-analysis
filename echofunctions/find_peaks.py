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
import glob

def calculateVolumesForEachFrame(videoName, outputFolderName, method):
    """Function to extract frames from input video file
    and save them as separate frames in an output directory.
    Args:
        videoName: Input video name.
        outputFolderName: Output directory to save the frames.
    Returns:
        None
    """

    root, df = loader.dataModules()
    volumeDict = {}

    frameIndices = df[df['FileName']==videoName]['Frame'].values
    frameIndices = [int(i) for i in frameIndices] 
    
    ES = min(frameIndices)
    ED = max(frameIndices)

    inputVideoPath = os.path.join(root, "segmented-videos", videoName + ".avi")
    outputPath = os.path.join(root, outputFolderName)

    os.makedirs(outputPath, exist_ok=True) # creates folder for frames of given video
        
    clipNumber, clipEnd = ES-1, ED # clip start, clip end
    
    cap = cv2.VideoCapture(inputVideoPath)
    cap.set(clipNumber, clipEnd)
    
    while cap.isOpened():
      ret, frame = cap.read()
      
      # Crop
      x1, y1, x2, y2 = 0, 0, 112, 112 # cropping coords and specs
      crop = frame[x1:x2, y1:y2]
      
      cv2.imwrite(os.path.join(outputPath, str((clipNumber+1)) + ".jpg"), crop)
      clipNumber += 1
      if (clipNumber is clipEnd):
        cap.release()
        break
    
    # Calculate Volumes
    for frame in os.listdir(outputPath):
      framePath = os.path.join(outputPath, frame)
      volumes, *_ = funcs.calculateVolume(framePath, 20, 0, method)
      volumeDict[os.path.splitext(frame)[0]] = volumes[0]
    
    return volumeDict

def returnPeaks(videoName="0X1BDEEC24D5FC570C", outputFolderName="find_peaks", method="Method of Disks"):
  volumeDict = calculateVolumesForEachFrame(videoName, outputFolderName, method)
  
  v=list(volumeDict.values())
  k=list(volumeDict.keys())

  ED_index = k[v.index(max(v))]
  ES_index = k[v.index(min(v))]

  return int(ES_index), int(ED_index)


print(returnPeaks())