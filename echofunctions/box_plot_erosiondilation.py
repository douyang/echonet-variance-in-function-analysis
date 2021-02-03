"""Echonet Function Evaluation comparisons of different
methods with erosion and dilation to compare the volume vs. ground truth"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import config
import loader
from algorithms import funcs as funcs
from algorithms import volume_tracings_calculations as tracings
from ast import literal_eval
from tqdm import tqdm

# Return dictionary of volume data with erosion and dilation using algorithms
def sortFrameVolumes(method, inputFolder, iterations):
  root, df = loader.dataModules()
  all_volumes={}

  exception_frames = 0

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolder) # frames path
  
  print("Calculating volumes for each frame with erosion and dilation")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] + ".avi" # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video
    
    if os.path.exists(FRAMES_PATH):
      try:
        volumes, *_ = funcs.calculateVolumeErosionAndDilation(FRAMES_PATH, 20, method=method, iterations=iterations)
        if videoName not in all_volumes and volumes is not "":
            all_volumes[videoName] = {}
            for r in range(-iterations, iterations, 1):
                all_volumes[videoName][r] = []
        
        for r in range(-iterations, iterations, 1):
            all_volumes[videoName][r].append(volumes[r])
      except:
        exception_frames += 1
    
  print(str(exception_frames) + " frames were not able to be calculated")

  return all_volumes

# Return dictionary of volume data calculated from coordinates given in VolumeTracings
def sortFrameVolumesFromTracings(method):
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  print("\Calculating volumes from VolumeTracings coordinates")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0] + ".avi"
    
    x1 = list(literal_eval(df.iloc[i, 2])) # x1 coords
    y1 = list(literal_eval(df.iloc[i, 3])) # y1 coords
    x2 = list(literal_eval(df.iloc[i, 4])) # x2 coords
    y2 = list(literal_eval(df.iloc[i, 5])) # y2 coords
    
    number = len(x1) - 1

    maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = tracings.calcParallelAndMaxPoints(x1, y1, x2, y2)

    if number < 22:
      if method == "Method of Disks":
        ground_truth_volume = funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Prolate Ellipsoid":
        ground_truth_volume = funcs.volumeProlateEllipsoidMethod(maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Bullet Method":
        ground_truth_volume = funcs.volumeBulletMethod(maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints)

      if videoName not in calculatedVolumeFromGroundTruth:
        calculatedVolumeFromGroundTruth[videoName] = []
      
      calculatedVolumeFromGroundTruth[videoName].append(ground_truth_volume)
  return calculatedVolumeFromGroundTruth

# Returns dictionary with calculated volumes (received from CSV)
def getCalculationsFromCSV(iterations):
  root, _ = loader.dataModules() # get path data
  calculatedVolumes = {}

  df = pd.read_csv(os.path.join(root, "Erosion and Dilation Volume Data.csv")) # reading in CSV
  df = df.astype(str).groupby(['Video Name']).agg(','.join).reset_index() # group based on file name

  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    
    for x in range((iterations * 2)):
      iteration = list(literal_eval((df.iloc[i, 2])))[x] # degree change
      calculatedESV = list(literal_eval((df.iloc[i, 4])))[x] # ESV calculation
      calculatedEDV = list(literal_eval((df.iloc[i, 5])))[x] # EDV calculation

      if videoName not in calculatedVolumes:
        calculatedVolumes[videoName] = {}
      if iteration not in calculatedVolumes[videoName]:
        calculatedVolumes[videoName][iteration] = [calculatedESV, calculatedEDV]
      
  return calculatedVolumes

# Return dictionary of volume data from FileList
def sortVolumesFromFileList(root=config.CONFIG.DATA_DIR):
  givenTrueDict={}

  df = pd.read_csv(os.path.join(root, "FileList.csv"), ) # reading in FileList.csv

  print("\Gathering volumes from FileList")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

# Compare volumes using calculated erosion and dilation iterations against FileList or VolumeTracings
def compareVolumePlot(inputFolder, method, volumeType, fromFile, iterations, useCSV, root=config.CONFIG.DATA_DIR):
  if useCSV:
    all_volumes = getCalculationsFromCSV(iterations)
  else:
    all_volumes = sortFrameVolumes(method, inputFolder, iterations)

  if fromFile is "VolumeTracings":
    true_volumes = sortFrameVolumesFromTracings(method)
  else:
    true_volumes = sortVolumesFromFileList()

  changesInVolumesDict = {}
  for iteration in range(-iterations, iterations, 1):
    changesInVolumesDict[iteration] = []

  for videoName in true_volumes:
    volumeData = true_volumes[videoName]

    ground_truth_ESV = min(volumeData) # true ESV value
    ground_truth_EDV = max(volumeData) # true EDV value
    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100 # true EF value (calculated)

    if videoName in all_volumes:
      for r in range(-iterations, iterations, 1):
        volumes = all_volumes[videoName][r] # volumes of given iteration

        EDV = max(all_volumes[videoName][0]) # calculated EDV for given iteration
        ESV = min(volumes) # calculated ESV for given iteration
        EF = (1 - (ESV/EDV)) * 100 # calculated EF for given iteration
        diff_EF = ((EF - ground_truth_EF)/ground_truth_EF) * 100 # difference in calculated EF and true EF
        diff_EDV = ((EDV-ground_truth_EDV)/ground_truth_EDV) * 100 # difference in calculated EDV and true EDV
        diff_ESV = ((ESV-ground_truth_ESV)/ground_truth_ESV) * 100 # difference in calculated ESV and true ESV
      
        if volumeType is "EF":
          changesInVolumesDict[r].append(diff_EF)
        elif volumeType is "ESV":
          changesInVolumesDict[r].append(diff_ESV)
        elif volumeType is "EDV":
          changesInVolumesDict[r].append(diff_EDV)

  return changesInVolumesDict

# Create box plot by calling functions and graphing data
def createBoxPlot(inputFolder="Masks_From_VolumeTracing", method="Method of Disks", volumeType="EF",
                  fromFile="FileList", iterations=5, useCSV=True):
  differenceInVolumes = compareVolumePlot(inputFolder, method, volumeType, fromFile, iterations, useCSV)
  labels = []

  for i in differenceInVolumes.keys():
    labels.append(i)

  # figure related code
  loader.latexify()
  fig = plt.figure()
  fig.suptitle('Comparison', fontsize=14, fontweight='bold')
  
  _, data = differenceInVolumes.keys(), differenceInVolumes.values()

  ax = fig.add_subplot(111)
  ax.boxplot(data, showfliers=False)

  #ax.set_title('Difference in Calculated ' + volumeType + ' against ' + fromFile + ' using Erosion and Dilation')
  ax.set_xlabel('% LV Area Decrease/Increase from Endocardial Tracing Error')

  if volumeType is "ESV" or volumeType is "EDV":
    ax.set_ylabel('% Change in ' + volumeType)
  else:
    ax.set_ylabel('% Change in Ejection Fraction')

  ax.set_xticklabels(labels)

  # show plot
  plt.show()

createBoxPlot(method="Method of Disks", volumeType="EF", inputFolder="frames", fromFile="FileList", iterations=5, useCSV=True)
#createBoxPlot(method="Method of Disks", volumeType="EF", inputFolder="frames", fromFile="VolumeTracings")
#createBoxPlot(method="Method of Disks", volumeType="ESV", inputFolder="frames", fromFile="VolumeTracings")
#createBoxPlot(method="Method of Disks", volumeType="EDV", inputFolder="frames", fromFile="VolumeTracings")