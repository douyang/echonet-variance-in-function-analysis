"""Echonet Function Evaluation statistical calculations for volumetric measurements"""

import pandas as pd
import os
import operator
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

def returnXAndYList():

  x, y = [], []
  df = pd.read_csv("/Users/ishan/Documents/Stanford/EchoData/Base Volume Data.csv") # reading in CSV

  for i in tqdm(range(len(df))): # iterates through each row of data frame
    EF = df.iloc[i, 6] # calculated EF
    ESV = df.iloc[i, 7] # calculated ESV
    EDV = df.iloc[i, 8] # calculated EDV

    true_EF = df.iloc[i, 3] # true EF
    true_ESV = df.iloc[i, 4] # true ESV
    true_EDV = df.iloc[i, 5] # true EDV

    x.append(EF)
    y.append(true_EF)
  
  return x, y

def returnRSquared(x, y):
  correlation_matrix = np.corrcoef(x, y)
  correlation_xy = correlation_matrix[0,1]
  r_squared = correlation_xy**2
  
  return r_squared

def mean_absolute_percentage_error(y_true, y_pred): 
  y_true, y_pred = np.array(y_true), np.array(y_pred)
  return str(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)

def scatterPlot():
  x1, y1 = returnXAndYList()

  x = np.array(x1)
  y = np.array(y1)
  
  m, b = np.polyfit(x, y, 1)

  plt.plot(x, y, 'o', alpha=0.8)
  plt.plot(x, m*x + b)
  print("Line of Best Fit: " + str(str(m) + "x" + " + " + str(b)))

  plt.title("Computerized Volumetric Calculations vs. True Volumes")
  plt.xlabel("Calculated Volume from Algorithms")
  plt.ylabel("True Volume")
  
  plt.show()

  slope, intercept, r_value, p_value, std_err = stats.linregress(x1, y1)
  rms = mean_squared_error(x1, y1, squared=False)
  mae = mean_absolute_error(y1, x1, multioutput='raw_values')

  print("Line: y = " + str(slope) + "x + " + str(intercept))
  print("R2: " + str(r_value**2))
  print("STD error: " + str(std_err))
  print("RMS: " + str(rms))
  print("MAE: " + str(mae[0]))
  print("MAPE: " + mean_absolute_percentage_error(y1, x1))

scatterPlot()

#print(returnRSquared())