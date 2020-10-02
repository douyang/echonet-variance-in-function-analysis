"""Echonet Function Evaluation comparisons of different methods'
 angle shifts to compare volume vs. ground truth on angle changes"""

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

def generateFrames(timing):
    """Loads a video from a file and returns cropped frame
    Args:
        timing (str): ESV or EDV
    """
    root, df = loader.dataModules()
    for i in range(len(df)//2):
        name = df.iloc[2*i, 0]
        frame = df.iloc[2*i, 1] if timing == "EDV" else df.iloc[2*i + 1, 1]
        for frameNum in range(frame-15, frame+16, 1):
            frameImage = loader.READ_AND_CROP_FRAME(name, frameNum)
            OUTPUT_FRAME_NAME = timing + "_" + name + "_" + str(frameNum) + ".png" # concatenate video name with frame number as file name
            frameImage.save(os.path.join(root, OUTPUT_FRAME_NAME))






# def sortFrameVolumes(method, inputFolder, sweeps):
#   root, df = loader.dataModules()
#   all_volumes={}

#   PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolder) # frames path
  
#   for i in range(len(df)): # iterates through each row of data frame
#     videoName = df.iloc[i, 0] # name of video
#     frameNumber = df.iloc[i, 1] # timing for clip
    
#     OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name

#     FRAMES_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # path to each video
    
#     if os.path.exists(FRAMES_PATH):
#       try:
#         volumes, x1, y1, x2, y2, degrees = funcs.calculateVolume(FRAMES_PATH, 20, sweeps, method)
#         if videoName not in all_volumes and volumes is not "":
#           all_volumes[videoName] = {}
#         for r in range(-(sweeps), sweeps+1, 1):
#           if r not in all_volumes[videoName]:
#             all_volumes[videoName][r] = [], []
          
#           all_volumes[videoName][r][0].append(volumes[r])
#           all_volumes[videoName][r][1].append(degrees[r])
#       except:
#         print(OUTPUT_FRAME_NAME)

#   return all_volumes

def sortFrameVolumesFromTracings(method):
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  for i in range(len(df)):
    videoName = df.iloc[i, 0]
    
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



# def createBoxPlot(inputFolder="Masks_From_VolumeTracing", method="Method of Disks", volumeType="EF",
#                   fromFile="FileList", normalized=True, sweeps=20):
#   changesInVolumesDict = compareVolumePlot(inputFolder, method, volumeType, fromFile, normalized, sweeps)
#   differenceInVolumes = {}
#   totalItems = 0

#   for key in changesInVolumesDict:
#     if key == 0:
#       bucket = (0, 0)
#     else:
#       residue = key % 5  
#       lowerBucketValue = key - residue
#       lowerBucketValue = lowerBucketValue - 180 if lowerBucketValue >= 90 else lowerBucketValue
#       lowerBucketValue = lowerBucketValue + 180  if lowerBucketValue < -90 else lowerBucketValue
#       upperBucketValue = lowerBucketValue + 5
#       bucket = (int(lowerBucketValue), int(upperBucketValue))

#     if abs(upperBucketValue + lowerBucketValue) < 120: 
#       if bucket not in differenceInVolumes:
#         differenceInVolumes[bucket] = []
#       differenceInVolumes[bucket] += changesInVolumesDict[key]
  
 
#   differenceInVolumes = list(differenceInVolumes.items())
#   differenceInVolumes.sort(key=lambda volumeShift: volumeShift[0][0] + volumeShift[0][1])

#   zeroItems = differenceInVolumes[len(differenceInVolumes)//2 + 1][1]
#   zeroItems.sort()
#   labels = [str(volumeShift[0]) for volumeShift in differenceInVolumes]
#   data = [volumeShift[1] for volumeShift in differenceInVolumes]

#   totalErr = 0
#   totalItems = 0
#   for sweep in differenceInVolumes:
#     bucket = sweep[0]
#     if abs(bucket[0] + bucket[1]) <= 15:
#       totalErr += sum([abs(shift) for shift in sweep[1]])
#       totalItems += len(sweep[1])
  
#   averageError = totalErr/totalItems
  
#   print("normalized: " + str(normalized))
#   print(volumeType)
#   print(fromFile)
#   print(averageError)
#   print(sweeps)

#   # figure related code
#   loader.latexify()
#   fig = plt.figure(figsize=(12, 8))
#   plt.xticks(fontsize=18)
#   plt.yticks(fontsize=18)


#   ax = fig.add_subplot(111)
#   ax.boxplot(data, showfliers=False)

#   ax.set_xticklabels(labels, Rotation=90)
  
#   # show plot
#   plt.savefig("./figures/paperBoxPlots/" + volumeType + ".png", bbox_inches='tight')
#   plt.show()

# # createBoxPlot(method="Method of Disks", volumeType="EF", inputFolder="Masks_From_VolumeTracing", 
# #               fromFile="FileList", normalized=True, sweeps=30)

# createBoxPlot(method="Method of Disks", volumeType="ESV", inputFolder="Masks_From_VolumeTracing", 
#               fromFile="VolumeTracings", normalized=True, sweeps=30)

# # createBoxPlot(method="Method of Disks", volumeType="EDV", inputFolder="Masks_From_VolumeTracing", 
# #               fromFile="VolumeTracings", normalized=True, sweeps=30)
