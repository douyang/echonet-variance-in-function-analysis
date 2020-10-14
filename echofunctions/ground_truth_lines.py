"""Creating masks of frames using ground truth
coordinates provided in VolumeTracings.csv"""

import pandas as pd
from ast import literal_eval
import os
import cv2
import loader
import tqdm

# Capture and Make Frames + Crop
def createMasks(inputFolderName="Masks_From_VolumeTracing", outputFolderName="Masks_From_VolumeTracing_Lines_From_VolumeTracing"):
  """Draws lines from ground truth coordinates on given masks
  """

  root, df = loader.dataModules()

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFolderName) # frames path
  PATH_TO_OUTPUT_DIR = os.path.join(root, outputFolderName) # frames path
  
  os.makedirs(PATH_TO_OUTPUT_DIR, exist_ok=True) # creates ground truth mask parent directory

  print("Drawing lines on each mask from VolumeTracings")
  for i in tqdm(range(len(df))): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip

    frameName = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name
    PATH_TO_RAW_FRAME = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, frameName)
    PATH_TO_OUTPUT_RAW_FRAME = os.path.join(PATH_TO_OUTPUT_DIR, frameName)

    image = cv2.imread(PATH_TO_RAW_FRAME) # read in the image from the specified frame path
    if os.path.exists(PATH_TO_RAW_FRAME): # checks if frame exists
      x1 = list(literal_eval(df.iloc[i, 2])) # x1 coords
      y1 = list(literal_eval(df.iloc[i, 3])) # y1 coords
      x2 = list(literal_eval(df.iloc[i, 4])) # x2 coords
      y2 = list(literal_eval(df.iloc[i, 5])) # y2 coords

      for coord in range(len(x1)): # iterate through each coordinate
        if coord is 0: # gets the perpendicular/long line
          longLine1stCoords = (int(x1[coord]), int(y1[coord]))
          longLine2ndCoords = (int(x2[coord]), int(y2[coord]))
        else: # draws the parallel lines
          cv2.line(image, (int(x1[coord]), int(y1[coord])), (int(x2[coord]), int(y2[coord])), (225, 25, 25), 1)
        
        cv2.line(image, longLine1stCoords, longLine2ndCoords, (321, 55, 145), 2) # Drawing the perpendicular/long line in different color

      cv2.imwrite(PATH_TO_OUTPUT_RAW_FRAME, image)

createMasks(inputFolderName="Masks_From_VolumeTracing", outputFolderName="Masks_From_VolumeTracing_Lines_From_VolumeTracing")