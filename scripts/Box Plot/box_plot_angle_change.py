"""Visualizing ablations on LVEF with slight rotations on main axis"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import operator
import collections
from ast import literal_eval
from tqdm import tqdm

# Returns dictionary with calculated volumes (received from CSV)
def getCalculationsFromCSV(sweeps):
  """Returns a dictionary from angle shift results in CSV
    Args:
        sweeps (int): Number of rotations to conduct

      Returns dictionary
    """
  calculatedVolumes = {}

  df = pd.read_csv("/Users/ishan/Documents/Stanford/EchoData/CSVs/Angle Shift.csv") # reading in CSV
  df = df.astype(str).groupby(['Video Name']).agg(','.join).reset_index() # group based on file name

  print("\nGathering data from CSV")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 1] # name of video
    
    for x in range((10 * 2) + 1):
      sweep = list(literal_eval((df.iloc[i, 2])))[x] # degree change
      ESV_angleshift = float(list(literal_eval((df.iloc[i, 3])))[x]) # ESV shift
      EDV_angleshift = float(list(literal_eval((df.iloc[i, 4])))[x]) # EDV shift
      calculatedESV = float(list(literal_eval((df.iloc[i, 5])))[x]) # ESV calculation
      calculatedEDV = float(list(literal_eval((df.iloc[i, 6])))[x]) # EDV calculation

      if videoName not in calculatedVolumes:
        calculatedVolumes[videoName] = {}
      if sweep not in calculatedVolumes[videoName]:
        calculatedVolumes[videoName][sweep] = [calculatedESV, calculatedEDV], [ESV_angleshift, EDV_angleshift]
  
  return calculatedVolumes

def createBoxPlot(method="Method of Disks", volumeType="EF", normalized=True, sweeps=20):
  """Exports CSV with left ventricle volumetric data with ablations
    Args:
        method (str): type of volumetric calculation to use
          Defaults to Method of Disks
        volumeType (str): the options of volume types are,
          ```EF``` (str): ejection fraction
          ```ESV``` (str): end-systolic volume
          ```EDV``` (str): end-diastolic volume

        normalized (bool): whether to normalize about the base volume or not
        sweeps (int): how many sweeps to capture from the CSV (must be <= actual amount of sweeps in CSV)
        
    """

  dataList = []
  changesInVolumesDict = {}

  results = getCalculationsFromCSV(sweeps)

  for videoName in results: # iterate through each video from true volumes dictionary
    volumeData = results[videoName] # get volumes from dictionary
    normal_ESV = min(volumeData[0][0]) # base ESV
    normal_EDV = max(volumeData[0][0]) # base EDV
    normal_EF = (1 - (normal_ESV/normal_EDV)) * 100 # base EF

    for sweep in volumeData: # iterate through shift in calculated volumes

      angleChanges = volumeData[sweep][1] # degrees of angle change for given shift
      if len(angleChanges) > 1:
        volumes = volumeData[sweep][0] # calculated volumes
       
        ESV = min(volumes) # given ESV
        EDV = max(volumes) # given EDV
        EF = (1 - (ESV/normal_EDV)) * 100 # given EF

        EDV_anglechange = angleChanges[volumes.index(max(volumes))] # EDV angle change
        ESV_anglechange = angleChanges[volumes.index(min(volumes))] # ESV angle change
        EF_anglechange = (angleChanges[0] + angleChanges[1])/2 # EF angle change is average of EDV and ESV angle change

        diff_EDV = ((EDV - normal_EDV)/normal_EDV) * 100 # difference in true and calculated EDV
        diff_ESV = ((ESV- normal_ESV)/normal_ESV) * 100 # difference in true and calculated ESV
        diff_EF = ((EF - normal_EF)/normal_EF) * 100 if normal_EF != 0 else 0 # difference in true and calculated EF

        if volumeType == "EF" and normal_EF != 0:
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
  print("Average Error: " + str(averageError))
  print("Sweeps: " + str(sweeps))

  # figure related code
  fig = plt.figure(figsize=(12, 8)) # create plt figure
  #plt.title(volumeType + " Volumes with Angle Shift against Volume Tracings' Coordinates") # set title
  plt.xticks(fontsize=8)
  plt.yticks(fontsize=8)


  plt.xlabel('Degrees of Rotation of the Longitudinal Axis')
  plt.ylabel('% Change in Ejection Fraction')

  ax = fig.add_subplot(111)
  ax.boxplot(data, showfliers=False)

  ax.set_xticklabels(labels, Rotation=90)
  
  # show plot
  plt.show()

createBoxPlot(method="Method of Disks", volumeType="EF", normalized=True, sweeps=2)
