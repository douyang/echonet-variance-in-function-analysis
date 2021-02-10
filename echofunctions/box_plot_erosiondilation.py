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

# Returns dictionary with calculated volumes (received from CSV)
def getCalculationsFromCSV(iterations, CSVName):
  root, _ = loader.dataModules() # get path data
  calculatedVolumes = {}

  df = pd.read_csv(os.path.join(root, CSVName)) # reading in CSV
  df = df.astype(str).groupby(['Video Name']).agg(','.join).reset_index() # group based on file name

  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    
    for x in range(-iterations, iterations):
      shift = list(literal_eval((df.iloc[i, 2])))[x] # degree change

      calculatedESV = float(list(literal_eval((df.iloc[i, 4])))[x]) # ESV calculation
      calculatedEDV = float(list(literal_eval((df.iloc[i, 5])))[x]) # EDV calculation

      if videoName not in calculatedVolumes:
        calculatedVolumes[videoName] = {}
      if shift not in calculatedVolumes[videoName]:
        calculatedVolumes[videoName][shift] = [calculatedESV, calculatedEDV]
  
  return calculatedVolumes

# Compare volumes using calculated main axis point shifts against FileList or VolumeTracings
def compareVolumePlot(method="Method of Disks", volumeType="EF", CSVName="Erosion and Dilation.csv", shifts=5, root=config.CONFIG.DATA_DIR):
  
  all_volumes = getCalculationsFromCSV(shifts, CSVName)

  changesInVolumesDict = {}

  for videoName in all_volumes:
    normal_volumes = all_volumes[videoName][0]

    normal_ESV = normal_volumes[0] # normal ESV value
    normal_EDV = normal_volumes[1] # normal EDV value
    
    zero_EF = (1 - (normal_ESV/normal_EDV)) * 100 # calculated EF for given point shift

    for shift in all_volumes[videoName].keys():
      if shift not in changesInVolumesDict:
        changesInVolumesDict[shift] = []
        
      volumes = all_volumes[videoName][shift] # volumes of given point shift

      ESV = volumes[0] # calculated ESV for given point shift
      EDV = volumes[1] # calculated EDV for given point shift
      EF = (1 - (ESV/EDV)) * 100 # calculated EF for given point shift

      diff_EF = ((EF - zero_EF)/zero_EF) * 100 # difference in calculated EF and true EF
      if 20 > shift > -20:
        if volumeType is "EF":
          changesInVolumesDict[shift].append(diff_EF)
  
  changesInVolumesDict = {k: v for k, v in changesInVolumesDict.items() if len(v) >= 50} # rmemoving shifts with low values
  changesInVolumesDict = {key:value for key, value in sorted(changesInVolumesDict.items(), key=lambda item: int(item[0]))} # sorting numerically

  createBoxPlot(changesInVolumesDict, volumeType)
  return changesInVolumesDict

# Create box plot by calling functions and graphing data
def createBoxPlot(differenceInVolumes, volumeType):
  
  # figure related code
  loader.latexify()
  fig, ax = plt.subplots()
  ax.boxplot(differenceInVolumes.values(), showfliers=False)
  ax.set_xticklabels(differenceInVolumes.keys())
  
  #ax.set_title('Difference in Calculated ' + volumeType + ' against ' + fromFile + ' using Erosion and Dilation')
  ax.set_xlabel('% LV Area Decrease/Increase from Endocardial Tracing Error')

  if volumeType is "ESV" or volumeType is "EDV":
    ax.set_ylabel('% Change in ' + volumeType)
  else:
    ax.set_ylabel('% Change in Ejection Fraction')

  # show plot
  plt.show()

compareVolumePlot(CSVName="Erosion and Dilation.csv", shifts=5)