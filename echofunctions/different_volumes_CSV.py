"""Creating output CSV data for different 
volume calculations for a video"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import loader
from algorithms import funcs as funcs
import config
from algorithms import volume_tracings_calculations as tracings
from ast import literal_eval
from tqdm import tqdm
import operator

# Returns dictionary of calculated volumes from algorithm
def calculateVolumesWithAlgorithm(method, inputFolderPath, task):
  root, df = loader.dataModules()
  calculatedData, failed_calculation = {}, 0

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderPath) # frames path
  
  print("\nCalculating volumes for both frames for each given video")
  
  df = pd.read_csv(os.path.join(root, "Frame Predictions.csv")) # reading in CSV

  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = os.path.splitext(df.iloc[i, 1])[0] # name of video
    ESV_frame = df.iloc[i, 2] # ESV timing
    EDV_frame = df.iloc[i, 3 ] # ESV timing

    ES_FRAME_FILENAME = str(ESV_frame) + ".jpg" # concatenate video name with frame number as file name
    ED_FRAME_FILENAME = str(EDV_frame) + ".jpg" # concatenate video name with frame number as file name

    ES_FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, videoName, ES_FRAME_FILENAME) # path to each video
    ED_FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, videoName, ED_FRAME_FILENAME) # path to each video
    
    if os.path.exists(ES_FRAMES_PATH) and os.path.exists(ED_FRAMES_PATH):
      try:
        ED_volumes, *_ = funcs.calculateVolumeMainAxisTopShift(ED_FRAMES_PATH, 20, pointShifts=1, method=method)

        if task == "Erosion and Dilation":
          ES_volumes, *_ = funcs.calculateVolumeErosionAndDilation(ES_FRAMES_PATH, 20, iterations=5, method=method)

        elif task == "Main Axis Top Shift":
          ES_volumes, *_ = funcs.calculateVolumeMainAxisTopShift(ES_FRAMES_PATH, 20, pointShifts=15, method=method)
          
        elif task == "Main Axis Bottom Shift":
          ES_volumes, *_ = funcs.calculateVolumeMainAxisBottomShift(ES_FRAMES_PATH, 20, pointShifts=15, method=method)
        
        elif task == "Angle Shift":
          ES_volumes, x1s, y1s, x2s, y2s, ES_degrees = funcs.calculateVolumeAngleShift(ES_FRAMES_PATH, 20, sweeps=10, method=method)
          ED_volumes, x1s, y1s, x2s, y2s, ED_degrees = funcs.calculateVolumeAngleShift(ED_FRAMES_PATH, 20, sweeps=10, method=method)

        for shift in ES_volumes: # each shift (key) in volumes
          if videoName not in calculatedData: # create sub-dictionary if video name not in dictionary
            calculatedData[videoName] = {}

          if shift not in calculatedData[videoName]: # create array if shift not in sub-dictionary 
            calculatedData[videoName][shift] = []

          if task == "Angle Shift":
            calculatedData[videoName][shift] = ([ES_volumes[shift], ES_degrees[shift]], [ED_volumes[shift], ED_degrees[shift]]) # add volumes for each shift and degrees for angle change
          else:
            calculatedData[videoName][shift] = [ES_volumes[shift], ED_volumes[0]] # add volumes for each shift
      except:
        failed_calculation += 1 # if exception case, add 1 (each frame unable to be calculated)

  print(str(failed_calculation) + " were not able to be calculated") # total number of exception frames
  
  return calculatedData

# Compare volumes from FileList against calculations
def compareVolumePlot(method="Method of Disks", inputFolderPath=None, fileName="angleSweeps.csv",
                      task="Erosion and Dilation"):
  
  calculatedData = calculateVolumesWithAlgorithm(method, inputFolderPath, task) # dictionary of all different coords

  dataList = []
  for videoName in calculatedData:
    volumes = calculatedData[videoName] # calculated volumes for given video
      
    for shift in volumes: # iterate through each shift (key in dictionary)
      ESV = volumes[shift][0] # calculated ESV
      EDV = volumes[shift][1] # calculated EDV

      if task == "Erosion and Dilation":
        EF = (1 - (ESV/EDV)) * 100 # calculated EF
        miniDict = {'Video Name': videoName, "Percent Change": shift, "Calculated EF": EF, "Calculated ESV": ESV,
                    "Calculated EDV": EDV}
      
      elif task == "Main Axis Top Shift" or task == "Main Axis Bottom Shift":
        EF = (1 - (ESV/EDV)) * 100 # calculated EF
        miniDict = {'Video Name': videoName, "Percent Change": int(shift * 100), "Calculated EF": EF, "Calculated ESV": ESV,
                    "Calculated EDV": EDV}
      
      elif task == "Angle Shift": # add degrees of angle change to dictionary
        ESV_rotation = ESV[1]
        EDV_rotation = EDV[1]

        ESV_calculation = ESV[0]
        EDV_calculation = EDV[0]
        EF_calculation = (1 - (ESV_calculation/EDV_calculation)) * 100

        miniDict = {'Video Name': videoName, "Iteration": shift, "ESV Rotation (Degrees)": ESV_rotation, "EDV Rotation (Degrees)": EDV_rotation,
                    "ESV": ESV_calculation, "EDV": EDV_calculation, "EF": EF_calculation}
      
      dataList.append(miniDict) # add the sub-dictionaries (each video)
      
  df = pd.DataFrame(dataList) # convert to dataframe
  export_path = os.path.join(config.CONFIG.DATA_DIR, fileName) # path to export

  df.to_csv(export_path) # export to CSV

compareVolumePlot(method="Method of Disks", inputFolderPath="find-peaks", fileName="Angle Shift.csv",
                  task="Angle Shift")