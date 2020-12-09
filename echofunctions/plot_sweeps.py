"""Echonet Function Evaluation to compare
predicted ES and ED frame against true"""

import find_peaks
import loader
import tqdm
import numpy as np
import matplotlib.pyplot as plt

def compareTrueAgainstPredicted(inputVideoFolderPath="segmented-videos"):
  root, df = loader.dataModules()
  ESDifferences, EDDifferences = [], []

  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    
    predictedIndices, trueIndices = find_peaks.returnPeaks(videoName=videoName, inputFolderName=inputVideoFolderPath)

    differenceInES, differenceInED = abs(trueIndices[0] - predictedIndices[0]), abs(trueIndices[1] - predictedIndices[1])
    
    ESDifferences.append(differenceInES)
    EDDifferences.append(differenceInED)
  
  createHistogram(ESDifferences, EDDifferences)

def createHistogram(ES_list, ED_list):
  x = [ES_list, ED_list]

  plt.hist(x, bins=2, histtype='step', align='mid', color=["g", "r"], label=["Differences in ES", "Differences in ED"])
  plt.legend(loc=2)
  plt.title('Timing Predictions vs. True Timings')
  plt.show()

compareTrueAgainstPredicted(inputVideoFolderPath="segmented-videos")