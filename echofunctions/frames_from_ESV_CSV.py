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

def returnTrueFrames(frames, x1, y1, x2, y2):
  volumesDict = {}
  for i in [0, 1]:
    number = len(x1[i]) - 1
    frameNumber = frames[i]

    maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(list(literal_eval(x1[i])), list(literal_eval(y1[i])), list(literal_eval(x2[i])), list(literal_eval(y2[i])))
    ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
    
    volumesDict[frameNumber] = ground_truth_volume

  ED = max(volumesDict.items(), key=operator.itemgetter(1))[0]
  ES = min(volumesDict.items(), key=operator.itemgetter(1))[0]

  return ED, ES

def calculateVolumesForEachFrame(videoName, inputFolderName, outputFolderName):
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

    x1 = df[df['FileName']==videoName]['X1'].values
    x2 = df[df['FileName']==videoName]['X2'].values
    y1 = df[df['FileName']==videoName]['Y1'].values
    y2 = df[df['FileName']==videoName]['Y2'].values

    true_ED, true_ES = returnTrueFrames(frameIndices, x1, y1, x2, y2) # returns ED and ES frame values

    inputVideoPath = os.path.join(root, inputFolderName, videoName + ".avi")
    outputPath = os.path.join(root, outputFolderName)
    currentVideoPath = os.path.join(outputPath, videoName)

    os.makedirs(outputPath, exist_ok=True) # creates parent directory for storing frames
    os.makedirs(currentVideoPath, exist_ok=True) # creates folder for each video under parent directory
    
    clipNumber, clipEnd = (true_ES - 15), (true_ES + 15) # clip start, clip end
    
    cap = cv2.VideoCapture(inputVideoPath)
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
    
    # EDV volume
    try:
      ED_framePath = os.path.join(outputPath, videoName, str(true_ED) + ".jpg")
      volumes, *_ = funcs.calculateVolumeMainAxisTopShift(ED_framePath, 20, pointShifts=1, method="Method of Disks") # 0th shift for regular volume
      ED_volume = volumes[0]
    except:
      ED_volume = 0

    # Calculate Volumes
    frameNumber = -15
    for frame in os.listdir(os.path.join(outputPath, videoName)):
      try:
        if videoName not in volumeDict:
          volumeDict[videoName] = {}
        
        ES_framePath = os.path.join(outputPath, videoName, frame)
        volumes, *_ = funcs.calculateVolumeMainAxisTopShift(ES_framePath, 20, pointShifts=1, method="Method of Disks") # 0th shift for regular volume
        volumeDict[videoName][frameNumber] = volumes[0]
      except:
        continue
    
    frameNumber += 1
    return volumeDict, ED_volume

# Returns dictionary of ejection fraction from FileList
def sortVolumesFromFileList(root=config.CONFIG.DATA_DIR):
  givenTrueDict={}

  df = pd.read_csv(os.path.join(root, "FileList.csv"), ) # reading in FileList.csv

  print("Calculating Ground Truth Values")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

def compareEjectionFraction(inputFolderName="segmented-videos", outputFolderName="ESV frame modulation",
                            fileName="Frame Differences from EDV Timing"):
  dataList = []
  true_dict = sortVolumesFromFileList()

  print("Calculating Volumes with Changes in ESV frames")
  for videoName in tqdm(true_dict):
    ground_truth_EF = true_dict[videoName]
    ES_volume, calculatedEDV = calculateVolumesForEachFrame(videoName, inputFolderName, outputFolderName)
    
    changesInVolumesDict = {"Video Name": videoName, "True EF": ground_truth_EF, "Calculated EDV": calculatedEDV}
    changesInVolumesDict.update(ES_volume)
  
  dataList.append(changesInVolumesDict)
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(config.CONFIG.DATA_DIR, fileName) # path to export

  df.to_csv(export_path) # export to CSV

compareEjectionFraction(inputFolderName="segmented-videos", outputFolderName="ESV frame modulation", fileName="Frame Differences from EDV Timing.csv")