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
from algorithms import volume_tracings_calculations as tracings
import glob

def returnTrueFrames(frames, x1, y1, x2, y2):
  try:
    volumesDict = {}
    for i in [0, 1]:
      number = len(x1[i]) - 1
      frameNumber = frames[i]

      maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(list(literal_eval(x1[i])), list(literal_eval(y1[i])), list(literal_eval(x2[i])), list(literal_eval(y2[i])))
      ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      
      volumesDict[frameNumber] = ground_truth_volume

    ED = max(volumesDict.items(), key=operator.itemgetter(1))[0]
    ES = min(volumesDict.items(), key=operator.itemgetter(1))[0]
  except:
    ED, ES = 0, 0

  return ED, ES

def calculateVolumesForEachFrame(videoName, inputFolderName, outputFolderName, makeFrames):
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
  failed_frames = 0

  # frameIndices = df[df['FileName']==videoName]['Frame'].values
  # frameIndices = [int(i) for i in frameIndices]

  # x1 = df[df['FileName']==videoName]['X1'].values
  # x2 = df[df['FileName']==videoName]['X2'].values
  # y1 = df[df['FileName']==videoName]['Y1'].values
  # y2 = df[df['FileName']==videoName]['Y2'].values

  # true_ED, true_ES = returnTrueFrames(frameIndices, x1, y1, x2, y2) # returns ED and ES frame values

  inputVideoPath = os.path.join(root, inputFolderName, videoName + ".avi")
  outputPath = os.path.join(root, outputFolderName)
  currentVideoPath = os.path.join(outputPath, videoName)

  os.makedirs(outputPath, exist_ok=True) # creates parent directory for storing frames
  os.makedirs(currentVideoPath, exist_ok=True) # creates folder for each video under parent directory
  
  if makeFrames:
    cap = cv2.VideoCapture(inputVideoPath)
    
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    clipNumber, clipEnd = 0, length - 1 # clip start, clip end
    cap.set(clipNumber, clipEnd)
    
    while cap.isOpened():
      ret, frame = cap.read()
      
      # Crop
      x1, y1, x2, y2 = 0, 0, 112, 112 # cropping coords and specs
      crop = frame[x1:x2, y1:y2]
      
      cv2.imwrite(os.path.join(outputPath, videoName, str((clipNumber)) + ".jpg"), crop)
      clipNumber += 1
      if (clipNumber is clipEnd):
        cap.release()
        break
  
  # Calculate Volumes
  for frame in os.listdir(os.path.join(outputPath, videoName)):
    #try:
    framePath = os.path.join(outputPath, videoName, frame)
    volumes, *_ = funcs.calculateVolumeMainAxisTopShift(framePath, 20, pointShifts=1, method="Method of Disks") # 0th shift for regular volume
    volumeDict[os.path.splitext(frame)[0]] = volumes[0]
    
    # except:
    #   failed_frames += 1
  
  print(volumeDict)
  return volumeDict

def returnPeaks(videoName="0X1BDEEC24D5FC570C", inputFolderName="Videos-Segmented", outputFolderName="find_peaks", makeFrames=True):

  volumeDict = calculateVolumesForEachFrame(videoName, inputFolderName, outputFolderName, makeFrames)

  if len(volumeDict) == 0:
    ES_index, ED_index = 0, 0
  else:
    v=list(volumeDict.values())
    k=list(volumeDict.keys())

    ED_index = k[v.index(max(v))]
    ES_index = k[v.index(min(v))]

  return int(ES_index), int(ED_index)
  
