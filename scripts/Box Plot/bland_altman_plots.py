"""Echonet Function Evaluation comparisons of algorithm
calculated volumes against truths in Bland Altman plots"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
import os
import math
import pyCompare
from tqdm import tqdm

def compareVolumePlot(root=config.CONFIG.DATA_DIR, pathToFrames="frames", method="Method of Disks",
                      volumeType="ESV", fromFile="VolumeTracings"):
  
  all_volumes = sortVolumesFromAlgo(pathToFrames, method)

  x, y = [], []
  
  if fromFile is "VolumeTracings":
    tracings_volumes = sortFrameVolumeTracings(method)
  else:
    tracings_volumes = sortVolumesFromFileList()

  for videoName in tracings_volumes:
    volumeData = tracings_volumes[videoName]
    ground_truth_ESV = min(volumeData)
    ground_truth_EDV = max(volumeData)
    ground_truth_EF = (1 - (ground_truth_ESV/ground_truth_EDV)) * 100

    if videoName in all_volumes:
      volumes = all_volumes[videoName]
      if len(volumes) > 1:
        EDV = max(volumes)
        ESV = min(volumes)

        EF = (1 - (ESV/EDV)) * 100
        
        if (EF - ground_truth_EF) > -25:
          if volumeType is "EF":
            x.append(EF)
            y.append(ground_truth_EF)
          elif volumeType is "ESV":
            x.append(EF)
            y.append(ground_truth_EF)

          elif volumeType is "EDV":
            x.append(EF)
            y.append(ground_truth_EF)
  
  if fromFile is "VolumeTracings":
    plt.title("EF from " + method + " Volumes of VolumeTracings vs. EF from Full Algorithm from Masks")
    plt.xlabel("Mean of " + method + " EF vs. VolumeTracings EF")
  else:
    plt.title("EF from FileList vs. EF from Full Algorithm from Masks")
    plt.xlabel("Mean of " + method + " EF vs. FileList EF")
  plt.show()