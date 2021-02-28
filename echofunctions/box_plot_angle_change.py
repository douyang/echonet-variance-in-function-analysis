"""Echonet Function Evaluation comparisons of different methods'
 angle shifts to compare volume vs. ground truth on angle shifts"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import operator
import config
import loader
from algorithms import funcs as funcs
from algorithms import volume_tracings_calculations as tracings
import collections
from ast import literal_eval
from tqdm import tqdm

# Returns dictionary with calculated volumes
def calculateAndSortVolumes(method, inputFolder, sweeps):
  root, df = loader.dataModules()
  calculatedVolumes={}

  exception_frames = 0
  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolder) # frames path
  
  print("Calculating volumes for each frame with a given angle change")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] + ".avi" # name of video
    frameNumber = df.iloc[i, 1] # timing for clip
    
    OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

    FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video
    
    if os.path.exists(FRAMES_PATH):
      try:
        volumes, x1, y1, x2, y2, degrees = funcs.calculateVolumeAngleShift(FRAMES_PATH, 20, sweeps=sweeps, method="Method of Disks")
    
        if videoName not in calculatedVolumes and volumes is not "": # create subdictionary if volumes not already in it and if not null
          calculatedVolumes[videoName] = {}
        for r in range(-(sweeps), sweeps+1, 1): # iterate through negative and positive keys
          if r not in calculatedVolumes[videoName]:
            calculatedVolumes[videoName][r] = [], [] # add two empty arrays if angle change not in subdictionary
          
          calculatedVolumes[videoName][r][0].append(volumes[r]) # add volumes from given shift
          calculatedVolumes[videoName][r][1].append(degrees[r]) # add degrees from given shift
      except:
        exception_frames += 1 # add to exception frames if frame was not able to be calculated
      
  print(str(exception_frames) + " were not able to be calculated")

  return calculatedVolumes

# Returns dictionary with calculated volumes (received from CSV)
def getCalculationsFromCSV(sweeps):
  root, _ = loader.dataModules() # get path data
  calculatedVolumes = {}

  df = pd.read_csv(os.path.join(root, "Intermediaries/Angle Shift.csv")) # reading in CSV
  df = df.astype(str).groupby(['Video Name']).agg(','.join).reset_index() # group based on file name

  print("\nGathering data from CSV")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    
    for x in range((sweeps * 2) + 1):
      sweep = list(literal_eval((df.iloc[i, 2])))[x] # degree change
      ESV_angleshift = float(list(literal_eval((df.iloc[i, 3])))[x]) # ESV shift
      EDV_angleshift = float(list(literal_eval((df.iloc[i, 4])))[x]) # EDV shift
      calculatedESV = float(list(literal_eval((df.iloc[i, 7])))[x]) # ESV calculation
      calculatedEDV = float(list(literal_eval((df.iloc[i, 8])))[x]) # EDV calculation

      if videoName not in calculatedVolumes:
        calculatedVolumes[videoName] = {}
      if sweep not in calculatedVolumes[videoName]:
        calculatedVolumes[videoName][sweep] = [calculatedESV, calculatedEDV], [ESV_angleshift, EDV_angleshift]
  
  return calculatedVolumes
# Returns dictionary of volumes calculated from VolumeTracings
def sortFrameVolumesFromTracings(method):
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  print("\nCalculating volumes from VolumeTracings coordinates")
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

# Returns dictionary of true volumes from FileList
def sortVolumesFromFileList(root=config.CONFIG.DATA_DIR):
  givenTrueDict={}

  df = pd.read_csv(os.path.join(root, "FileList.csv"), ) # reading in FileList.csv
  
  print("\nGathering volumes from FileList")
  for i in tqdm(range(len(df))):
    videoName = df.iloc[i, 0]
    ground_truth_ESV = df.iloc[i, 2]
    ground_truth_EDV = df.iloc[i, 3]

    if videoName not in givenTrueDict:
      givenTrueDict[videoName] = []
    
    givenTrueDict[videoName] = [ground_truth_ESV, ground_truth_EDV]

  return givenTrueDict

# Compare volumes from calculations against true volumes
def compareVolumePlot(inputFolder, method, volumeType, fromFile, normalized, sweeps, useCSV, root=config.CONFIG.DATA_DIR):
  
  dataList = []
  if useCSV == True:
    all_volumes = getCalculationsFromCSV(sweeps)
  
  else:
    all_volumes = calculateAndSortVolumes(method, inputFolder, sweeps) # get dictionary of calculated volumes

  # Get true volumes from VolumeTracings or FileList
  if fromFile is "VolumeTracings":
    true_volumes = sortFrameVolumesFromTracings(method)
  else:
    true_volumes = sortVolumesFromFileList()

  changesInVolumesDict = {}

  for videoName in true_volumes: # iterate through each video from true volumes dictionary
    volumeData = true_volumes[videoName] # get volumes from dictionary

    ground_truth_ESV = min(volumeData) # true ESV value
    ground_truth_EDV = max(volumeData) # true EDV value
    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100 # true EF value

    if videoName in all_volumes: # check if video in calculated volumes' dictionary
      normal_EDV = max(all_volumes[videoName][0][0]) # zeroth EDV (keep constant)
      normal_ESV = min(all_volumes[videoName][0][0]) # calculated ESV value
      normal_EF = (1 - (normal_ESV/normal_EDV)) * 100 # calculated EF value
      
      for angleShift in all_volumes[videoName]: # iterate through shift in calculated volumes
        angleChanges = all_volumes[videoName][angleShift][1] # degrees of angle change for given shift
        if len(angleChanges) > 1:
          volumes = all_volumes[videoName][angleShift][0] # calculated volumes
          
          #EDV = max(volumes) # calculated EDV value
          EDV = max(all_volumes[videoName][0][0]) # zeroth EDV (keep constant)
          ESV = min(volumes) # calculated ESV value
          EF = (1 - (ESV/normal_EDV)) * 100 # calculated EF value

          EDV_anglechange = angleChanges[volumes.index(max(volumes))] # EDV angle change
          ESV_anglechange = angleChanges[volumes.index(min(volumes))] # ESV angle change
          EF_anglechange = (angleChanges[0] + angleChanges[1])/2 # EF angle change is average of EDV and ESV angle change

          diff_EDV = ((EDV-ground_truth_EDV)/ground_truth_EDV) * 100 # difference in true and calculated EDV
          diff_ESV = ((ESV-ground_truth_ESV)/ground_truth_ESV) * 100 # difference in true and calculated ESV
          diff_EF = ((EF - normal_EF)/normal_EF) * 100 if normal_EF != 0 else 0 # difference in true and calculated EF

          if volumeType == "EF" and ground_truth_EF != 0:
            if int(EF_anglechange) not in changesInVolumesDict:
              changesInVolumesDict[int(EF_anglechange)] = [] # create empty array in dictionary
            
            changesInVolumesDict[int(EF_anglechange)].append(diff_EF) # add difference in EF

            volumesWithRotations = {"Video Name": videoName, "EF Change (Percent)": diff_EF, "Degree of Rotation": ESV_anglechange, "ESV": ESV, "Normal EDV": normal_EDV, "Calculated EF": EF}
            dataList.append(volumesWithRotations)
            
          elif volumeType == "ESV":
            if int(ESV_anglechange) not in changesInVolumesDict:
              changesInVolumesDict[int(ESV_anglechange)] = []  # create empty array in dictionary
            
            changesInVolumesDict[int(ESV_anglechange)].append(diff_ESV) # add difference in ESV

          elif volumeType == "EDV":
            if int(EDV_anglechange) not in changesInVolumesDict:
              changesInVolumesDict[int(EDV_anglechange)] = []  # create empty array in dictionary
            
            changesInVolumesDict[int(EDV_anglechange)].append(diff_EDV) # add difference in EDV

  if normalized:
    zeroItems = changesInVolumesDict[0] # get zeroth values
    zeroItems.sort()
    shift = zeroItems[len(zeroItems)//2]
    print("Shift" + str(shift))

    for angle in changesInVolumesDict:
      for i in range(len(changesInVolumesDict[angle])):
        changesInVolumesDict[angle][i] -= shift
  
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(config.CONFIG.DATA_DIR, "Angle Shift EF Change.csv") # path to export

  df.to_csv(export_path) # export to CSV

  return changesInVolumesDict

def createBoxPlot(inputFolder="Masks_From_VolumeTracing", method="Method of Disks", volumeType="EF",
                  fromFile="FileList", normalized=True, sweeps=20, useCSV=True):
  
  changesInVolumesDict = compareVolumePlot(inputFolder, method, volumeType, fromFile, normalized, sweeps, useCSV)
  differenceInVolumes = {}
  totalItems = 0

  # Bucketing algorithm to bucket based off of degrees
  for key in changesInVolumesDict:
    if key == 0:
      bucket = (0, 0)
    else:
      residue = key % 5  
      lowerBucketValue = key - residue
      lowerBucketValue = lowerBucketValue - 180 if lowerBucketValue >= 90 else lowerBucketValue
      lowerBucketValue = lowerBucketValue + 180  if lowerBucketValue < -90 else lowerBucketValue
      upperBucketValue = lowerBucketValue + 5
      bucket = (int(lowerBucketValue), int(upperBucketValue))

    if abs(upperBucketValue + lowerBucketValue) < 120: 
      if bucket not in differenceInVolumes:
        differenceInVolumes[bucket] = []
      differenceInVolumes[bucket] += changesInVolumesDict[key]
  
  differenceInVolumes = list(differenceInVolumes.items())
  differenceInVolumes.sort(key=lambda volumeShift: volumeShift[0][0] + volumeShift[0][1])

  zeroItems = differenceInVolumes[len(differenceInVolumes)//2 + 1][1]
  zeroItems.sort()
  labels = [str(volumeShift[0]) for volumeShift in differenceInVolumes]
  data = [volumeShift[1] for volumeShift in differenceInVolumes]

  totalErr = 0
  totalItems = 0
  for sweep in differenceInVolumes:
    bucket = sweep[0]
    if abs(bucket[0] + bucket[1]) <= 15:
      totalErr += sum([abs(shift) for shift in sweep[1]])
      totalItems += len(sweep[1])
  
  averageError = totalErr/totalItems
  
  print("Normalized: " + str(normalized))
  print("Volume Type: " + str(volumeType))
  print("Comparison with: " + str(fromFile))
  print("Average Error: " + str(averageError))
  print("Sweeps: " + str(sweeps))

  # figure related code
  loader.latexify() # latexify the graphs
  fig = plt.figure(figsize=(12, 8)) # create plt figure
  #plt.title(volumeType + " Volumes with Angle Shift against Volume Tracings' Coordinates") # set title
  plt.xticks(fontsize=8)
  plt.yticks(fontsize=8)

  #plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1)) # sets percentages for y-axis

  plt.xlabel('Degrees of Rotation of the Longitudinal Axis')
  plt.ylabel('% Change in Ejection Fraction')

  ax = fig.add_subplot(111)
  ax.boxplot(data, showfliers=False)

  ax.set_xticklabels(labels, Rotation=90)
  
  # show plot
  plt.savefig("./figures/paperBoxPlots/" + volumeType + ".png", bbox_inches='tight')
  plt.show()

createBoxPlot(method="Method of Disks", volumeType="EF", inputFolder="frames", 
              fromFile="VolumeTracings", normalized=True, sweeps=15, useCSV=True)
