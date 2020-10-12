"""Utility functions for videos, frame captures, plotting."""

import pandas as pd
from ast import literal_eval
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import config

# Returns paths for frame captures
def dataModules(root=None):
  """Loads a video from a file
    Args:
        root (str): The path to where the data is stored.
            Defaults to data directory specified in config file.
    Returns:
        Path list that contains root, segmented videos path, and 
        a grouped data frame
    """

  if root is None:
    root = config.CONFIG.DATA_DIR
  
  df = pd.read_csv(os.path.join(root, "VolumeTracings.csv")) # reading in VolumeTracings.csv
  df = df.astype(str).groupby(['FileName', 'Frame']).agg(','.join).reset_index() # group VolumeTracings.csv by FileName and Frame timing

  return root, df

def READ_AND_CROP_FRAME(videoPath: str, timing: int, makeCrop=True):
  """Loads a video from a file and returns cropped frame
    Args:
        videoPath (str): The path to the video/clip
        timing (int): The frame number that needs to be read
    Returns:
        Cropped image based e coords and height, width
    """
  cap = cv2.VideoCapture(videoPath) # Create VideoCapture object

  cap.set(1, int(timing)) # sets to capture specific frame
  ret, frame = cap.read()
  
  h, w, c = frame.shape # get frame data types
  
  x1, y1, x2, y2 = 0, 0, 112, 112 # cropping coords and specs

  # Crop
  crop = frame[x1:x2, y1:y2]

  if makeCrop:
    return crop
  else:
    return frame

def scatterPlot(title="Plot", xlabel="", ylabel="", x1=[], y1=[], lineOfBestFit=True, alpha=0.5):
  x = np.array(x1)
  y = np.array(y1)
  
  latexify()
  if lineOfBestFit:
    m, b = np.polyfit(x, y, 1)

    plt.plot(x, y, 'o', alpha=alpha)
    plt.plot(x, m*x + b)
    print("Line of Best Fit: " + str(str(m) + "x" + " + " + str(b)))
  else:
    plt.scatter(x, y, alpha=0.5)
    
  plt.title(title)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.show()

  r_squared = calculatePlotData(x1, y1)
  print("R2: " + str(r_squared))

def latexify():
  """Sets matplotlib params to appear more like LaTeX.

  Based on https://nipunbatra.github.io/blog/2014/latexify.html
  """
  params = {'backend': 'pdf',
            'axes.titlesize': 8,
            'axes.labelsize': 8,
            'font.size': 8,
            'legend.fontsize': 8,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'font.family': 'DejaVu Serif',
            'font.serif': 'Computer Modern',
            }
  plt.rcParams.update(params)

def calculatePlotData(x, y):
  """Calculated statistical data from calculations
    Args:
        x (list): list of x values
        y (list): list of y values
    Returns:
        The r-squared statistical value
    """

  correlation_matrix = np.corrcoef(x, y)
  correlation_xy = correlation_matrix[0,1]
  r_squared = correlation_xy**2
  
  return r_squared

def loadvideo(filename: str) -> np.ndarray:
    """Loads a video from a file.
    Args:
        filename (str): filename of video
    Returns:
        A np.ndarray with dimensions (channels=3, frames, height, width). The
        values will be uint8's ranging from 0 to 255.
    Raises:
        FileNotFoundError: Could not find `filename`
        ValueError: An error occurred while reading the video
    """

    if not os.path.exists(filename):
        raise FileNotFoundError(filename)
    capture = cv2.VideoCapture(filename)

    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    v = np.zeros((frame_count, frame_width, frame_height, 3), np.uint8)

    for count in range(frame_count):
        ret, frame = capture.read()
        if not ret:
            raise ValueError("Failed to load frame #{} of {}.".format(count, filename))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        v[count] = frame

    v = v.transpose((3, 0, 1, 2))

    return v

def returnSTD(CSV_PATH, axis=0):
  df = pd.read_csv(CSV_PATH)

  return str(df.std(axis=axis, skipna=True))
