"""Assessing difference in ejection
fraction with changes in ESV timings"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import operator
import config
import loader
from algorithms import funcs as funcs
from algorithms import volume_tracings_calculations as tracings
from algorithms import normalizations as normalize
import collections
import cv2
from ast import literal_eval
from tqdm import tqdm

# Returns dictionary of calculated volumes from algorithm
def calculateVolumesWithAlgorithm(method, inputFolderPath):
  root, df = loader.dataModules()
  calculatedData, failed_calculation = {}, 0

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderPath) # frames path
  
  dataList = []
  print("\nCalculating volumes for EDV frames for each given video")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    if (i % 2) is 0:
      CSVData = {}

      videoName = df.iloc[i, 0] + ".avi" # name of video
      frameNumber = df.iloc[i, 1] # timing for clip
      
      # Finds EDV
      frameIndices = df[df['FileName']==df.iloc[i, 0]]['Frame'].values
      frameIndices = [int(i) for i in frameIndices]

      x1 = df[df['FileName']==df.iloc[i, 0]]['X1'].values
      x2 = df[df['FileName']==df.iloc[i, 0]]['X2'].values
      y1 = df[df['FileName']==df.iloc[i, 0]]['Y1'].values
      y2 = df[df['FileName']==df.iloc[i, 0]]['Y2'].values

      volumesDict = {}
      for i in [0, 1]:
        number = 20
        frameNumber = frameIndices[i]

        maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(list(literal_eval(x1[i])), list(literal_eval(y1[i])), list(literal_eval(x2[i])), list(literal_eval(y2[i])))
        ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
        
        volumesDict[frameNumber] = ground_truth_volume

      ED = max(volumesDict.items(), key=operator.itemgetter(1))[0]

      ED_FRAME_FILENAME = videoName + "_" + str(ED) + ".png" # concatenate video name with frame number as file name

      ED_FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, ED_FRAME_FILENAME) # path to each video
      if os.path.exists(ED_FRAMES_PATH):
        try:
          ED_volumes, x1s, y1s, x2s, y2s = funcs.calculateVolumeErosionAndDilation(ED_FRAMES_PATH, 20, iterations=1, method=method)
          if videoName not in calculatedData: # create sub-dictionary if video name not in dictionary
            calculatedData[videoName] = {}

          calculatedData[videoName] = ED_volumes[0] # add volumes for each shift

          CSVData = {"Video Name": videoName, "EDV Volume": ED_volumes[0]}
          dataList.append(CSVData)
        except:
          failed_calculation += 1 # if exception case, add 1 (each frame unable to be calculated)

  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(config.CONFIG.DATA_DIR, "EDV Data.csv") # path to export

  df.to_csv(export_path) # export to CSV
  print(str(failed_calculation) + " were not able to be calculated") # total number of exception frames
  
  return calculatedData

# Returns dictionary with calculated volumes (received from CSV)
def getCalculationsFromCSV(CSV_NAME, frameDifference=15):
  root, _ = loader.dataModules() # get path data
  calculatedVolumes = {}

  df = pd.read_csv(os.path.join(root, "CSVs", CSV_NAME)) # reading in CSV
  df = df.astype(str).groupby(['Video Name']).agg(','.join).reset_index() # group based on file name

  print("\nGathering volumes from CSV calculations")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    currentFrameDifference = -frameDifference - 1 # starts at frame difference
    videoName = df.iloc[i, 0] # name of video
    
    for frame in range((frameDifference * 2) + 1):
      currentFrameDifference += 1
      calculatedESV = float(df.iloc[i, frame + 2]) # ESV calculation

      if videoName not in calculatedVolumes:
        calculatedVolumes[videoName] = {}
      if currentFrameDifference not in calculatedVolumes[videoName]:
        calculatedVolumes[videoName][currentFrameDifference] = calculatedESV
  
  return calculatedVolumes

# Returns dictionary with calculated EDV volumes (received from CSV)
def returnEDVData():
  root, _ = loader.dataModules() # get path data
  calculatedVolumes = {}

  df = pd.read_csv(os.path.join(root, "EDV Data.csv")) # reading in CSV

  print("\nGathering volumes from CSV calculations")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 1] # name of video
    calculatedESV = float(df.iloc[i, 2]) # ESV calculation

    calculatedVolumes[videoName] = calculatedESV

  return calculatedVolumes

# Compare volumes using calculated erosion and dilation iterations against FileList or VolumeTracings
def compareVolumePlot(CSV_NAME="esvTimingSweeps.csv", method="Method of Disks", volumeType="EF",
                      fromFile="VolumeTracings", frameDifference=5, root=config.CONFIG.DATA_DIR):
  
  zero_normal_EF = 0

  ES_volumes = getCalculationsFromCSV(CSV_NAME)
  ED_volumes = returnEDVData()
  #ED_volumes = calculateVolumesWithAlgorithm(method, "frames")

  changesInVolumesDict = {}

  for videoName in ES_volumes:
    if videoName in ED_volumes:
      normal_ESV = ES_volumes[videoName][0] # volumes of given iteration
      normal_EDV = ED_volumes[videoName]
      
      normal_EF = (1 - (normal_ESV/normal_EDV)) * 100 # calculated EF for given iteration

      if normal_EF != 0:
        for r in range(-5, 6):
          if r not in changesInVolumesDict:
            changesInVolumesDict[r] = []
          
          #print(changesInVolumesDict)
          ESV = ES_volumes[videoName][r] # volumes of given iteration
          EF = (1 - (ESV/normal_EDV)) * 100 # calculated EF for given iteration

          diff_EF = ((EF - normal_EF)/normal_EF) * 100 # difference in calculated EF and true EF

          if volumeType is "EF" and diff_EF > -100:
            changesInVolumesDict[r].append(diff_EF)
      else:
        zero_normal_EF += 1

  print(changesInVolumesDict.keys())
  print(zero_normal_EF)
  
  createBoxPlot(changesInVolumesDict, volumeType)

# Create box plot by calling functions and graphing data
def createBoxPlot(differenceInVolumes, volumeType):
  
  # figure related code
  loader.latexify()
  fig, ax = plt.subplots()
  ax.boxplot(differenceInVolumes.values(), showfliers=False)
  ax.set_xticklabels(differenceInVolumes.keys())
  
  #ax.set_title('Difference in Calculated ' + volumeType + ' against ' + fromFile + ' using Erosion and Dilation')
  ax.set_xlabel('Number of frames off from true ESV')

  if volumeType is "ESV" or volumeType is "EDV":
    ax.set_ylabel('% Change in ' + volumeType)
  else:
    ax.set_ylabel('% Change in Ejection Fraction')

  # show plot
  plt.show()

compareVolumePlot(CSV_NAME="Frame Differences from EDV Timing.csv", method="Method of Disks", volumeType="EF",
                      fromFile="VolumeTracings", frameDifference=6)