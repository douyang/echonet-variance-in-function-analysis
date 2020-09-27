"""Echonet Function Evaluation comparisons of volume calculated from coordinates
given in VolumeTracings against given volume calculations in FileList"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
import os
import math
import config
import loader
import algorithms

def sortFrameVolumes(method):
  _, df = loader.dataModules()
  calculatedVolumeFromGroundTruth={}
  
  for i in range(len(df)):
    videoName = df.iloc[i, 0]
    
    x1 = list(literal_eval(df.iloc[i, 2])) # x1 coords
    y1 = list(literal_eval(df.iloc[i, 3])) # y1 coords
    x2 = list(literal_eval(df.iloc[i, 4])) # x2 coords
    y2 = list(literal_eval(df.iloc[i, 5])) # y2 coords
    
    number = len(x1) - 1

    maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints = algorithms.volume_tracings_calculations.calcParallelAndMaxPoints(x1, y1, x2, y2)

    if number < 22:
      if method == "Method of Disks":
        ground_truth_volume = algorithms.funcs.volumeMethodOfDisks(maxX1, maxY1, maxX2, maxY2, number, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Prolate Ellipsoid":
        ground_truth_volume = algorithms.funcs.volumeProlateEllipsoidMethod(maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints)
      elif method == "Bullet Method":
        ground_truth_volume = algorithms.funcs.volumeBulletMethod(maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints)

      if videoName not in calculatedVolumeFromGroundTruth:
        calculatedVolumeFromGroundTruth[videoName] = []
      
      calculatedVolumeFromGroundTruth[videoName].append(ground_truth_volume)
  return calculatedVolumeFromGroundTruth

def compareVolumePlot(root=config.CONFIG.DATA_DIR, method="Method of Disks", timing="ESV"):
  volumes = sortFrameVolumes(method)
  x, y = [], []
  count=0

  df = pd.read_csv(os.path.join(root, "FileList.csv"), ) # reading in VolumeTracings.csv

  for i in range(len(df)):
    videoName = df.iloc[i, 0]

    ground_EF = df.iloc[i, 1]
    ground_ESV = df.iloc[i, 2]
    ground_EDV = df.iloc[i, 3]

    if videoName in volumes and (len(volumes[videoName]) > 1):
      timings = volumes[videoName]
      
      EDV = max(timings)
      ESV = min(timings)
      
      EF = (1 - (ESV/EDV)) * 100

      if abs(EF - ground_EF) > 15:
        print([videoName, ground_EF, EF])

      if timing is "EDV":
        x.append(EDV)
        y.append(ground_EDV)
      elif timing is "ESV":
        x.append(ESV)
        y.append(ground_ESV)

      elif timing is "EF":
        count+=1
        x.append(EF)
        y.append(ground_EF)

  print(count)
  title = 'Line From VolumeTracings ' + timing + ' vs. FileList ' + timing
  xlabel = 'Line from VolumeTracings ' + '(' + method + ')'
  ylabel = 'Ground Truth' + timing + ' From FileList'
  loader.scatterPlot(title=title, xlabel=xlabel, ylabel=ylabel, x1=x, y1=y, lineOfBestFit=True)

compareVolumePlot(timing="EF")