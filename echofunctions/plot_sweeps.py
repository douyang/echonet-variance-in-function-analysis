"""Echonet Function Evaluation to find
EDV and ESV frame indices for given video"""

from ast import literal_eval
import loader
from algorithms import find_peaks
import tqdm
from algorithms import funcs
from algorithms import volume_tracings_calculations as tracings
import config
import pandas as pd
import os

def sortFrameVolumes(method="Method of Disks"):
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  print("Calculating ground truth volumes from VolumeTracings")
  for i in range(len(df)):
    videoName = df.iloc[i, 0]
    
    x1 = list(literal_eval(df.iloc[i, 2])) # x1 coords
    y1 = list(literal_eval(df.iloc[i, 3])) # y1 coords
    x2 = list(literal_eval(df.iloc[i, 4])) # x2 coords
    y2 = list(literal_eval(df.iloc[i, 5])) # y2 coords
    frame = df.iloc[i, 1] # frame number
    
    number = len(x1) - 1

    maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(x1, y1, x2, y2)

    if number < 22:
      if method == "Method of Disks":
        ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      
      if videoName not in calculatedVolumeFromGroundTruth:
        calculatedVolumeFromGroundTruth[videoName] = {}
      
      calculatedVolumeFromGroundTruth[videoName][frame] = ground_truth_volume
  return calculatedVolumeFromGroundTruth

def comparePredictedTimingAgainstTrue(fileName):
  _, df = loader.dataModules()
  dataList = []
  trueVolumes = sortFrameVolumes()
  print(trueVolumes)
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0] # name of video
    
    # Get true frame index values
    v=list(trueVolumes[videoName].values())
    k=list(trueVolumes[videoName].keys())
    true_EDV = int(k[v.index(max(v))])
    true_ESV = int(k[v.index(min(v))])

    # Gather predicted EDV and ESV timing frames
    ESV_index, EDV_index = find_peaks.returnPeaks(videoName=videoName+".avi")

    # Calculate Differences
    differenceInEDV = abs(true_EDV - EDV_index)
    differenceInESV = abs(true_ESV - ESV_index)

    miniDict = {'Video Name': videoName, "Predicted ESV Frame": ESV_index, 'Predicted EDV Frame': EDV_index, 'True ESV Frame': true_ESV, 'True EDV Frame': true_EDV, 'Difference in ESV Frame': differenceInESV, 'Difference in EDV Frame': differenceInEDV}

    dataList.append(miniDict)

  df = pd.DataFrame(dataList)
  export_path = os.path.join(config.CONFIG.DATA_DIR, fileName)
  df.to_csv(export_path)

comparePredictedTimingAgainstTrue("prediction-sweeps.csv")