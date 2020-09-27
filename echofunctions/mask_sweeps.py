"""Echonet Function Evaluation masks with
different sweeps on point shifts"""

import pandas as pd
from ast import literal_eval
import os
import cv2
from algorithms import funcs as funcs
import loader

# Capture and Make Frames + Crop
def capture(method, inputFramesFolder, outputFramesFolder, masksWithMoreThan21Lines, sweepsOfMoreThan21Lines):

  PATH_DATA = [] # list that contains path information (later used for masks)
  root, df = loader.dataModules()

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, inputFramesFolder)
  PATH_TO_MASK_FRAMES_PARENT_DIR = os.path.join(root, outputFramesFolder)
  
  os.makedirs(PATH_TO_RAW_FRAMES_PARENT_DIR, exist_ok=True) # creates frames parent directory
  os.makedirs(PATH_TO_MASK_FRAMES_PARENT_DIR, exist_ok=True) # creates mask parent directory

  if sweepsOfMoreThan21Lines:
    for FRAME_FILENAME in (os.listdir(os.path.join(root, masksWithMoreThan21Lines))):
      PATH_TO_FRAME = os.path.join(os.path.join(root, masksWithMoreThan21Lines), FRAME_FILENAME)
    
      PATH_DATA.append([PATH_TO_FRAME, PATH_TO_MASK_FRAMES_PARENT_DIR, FRAME_FILENAME])
  else:
    for i in range(len(df)): # iterates through each row of data frame
      videoName = df.iloc[i, 0] # name of video
      frameNumber = df.iloc[i, 1] # timing for clip

      FRAME_FILENAME = videoName + "_" + str(frameNumber) + ".png" # concatenate video name with frame number as file name
      PATH_TO_FRAME = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, FRAME_FILENAME) # (data directory)/frames/(file name)

      if (os.path.exists(PATH_TO_FRAME)):
        PATH_DATA.append([PATH_TO_FRAME, PATH_TO_MASK_FRAMES_PARENT_DIR, FRAME_FILENAME])
      
  return PATH_DATA

def generateMasks(method="Method of Disks", testImages="all", 
                  inputFramesFolder="Masks_From_VolumeTracing", outputFramesFolder="angle_sweeps",
                  masksWithMoreThan21Lines="21LinesMasks", sweepsOfMoreThan21Lines=False):
  """Mask generation code to execute capture frames and generate ejection fraction masks
    Args:
        method (str): Mathematical formula/method to use
            If method is not supported, Raise Error
            Defaults to Method of Disks.
        testImages: How many different frames to create sweeps for
            Defaults to all.
        inputFramesFolder (str): path to input raw frames to assess
        outputFramesFolder (str): sweeps folder to output
        masksWithMoreThan21Lines (str): path to input raw frames with
                                        more than 21 lines specifically 
        sweepsOfMoreThan21Lines (bool): whether or not to create sweeps for tracings with more
                                        than 21 lines
            Defaults to False        
    """
  PATH_DATA = capture(method, inputFramesFolder, outputFramesFolder, masksWithMoreThan21Lines, sweepsOfMoreThan21Lines)

  if testImages is not "all":
    PATH_DATA = PATH_DATA[0 : testImages]
  
  for frame in PATH_DATA:
    try:
      volumes, x1, y1, x2, y2, degrees = funcs.calculateVolume(frame[0], 20, method)

      for angleShift in x1:
        MASK_OUTPUT_PATH = os.path.join(frame[1], str(angleShift) + "_" + frame[2]) # join parent path (root) with mask output name
        image = cv2.imread(frame[0]) # read in the image from the specified frame path
        
        for coord in range(len(x1[angleShift])): # iterate through each coordinate
          if coord is 0: # gets the perpendicular/long line
            longLine1stCoords = (x1[angleShift][coord], y1[angleShift][coord])
            longLine2ndCoords = (x2[angleShift][coord], y2[angleShift][coord])
          else:
            cv2.line(image, (x1[angleShift][coord], y1[angleShift][coord]), (x2[angleShift][coord], y2[angleShift][coord]), (177, 125, 125), 1)
            
        cv2.line(image, longLine1stCoords, longLine2ndCoords, (31, 55, 145), 2) # Drawing the perpendicular/long line in different color

        cv2.imwrite(MASK_OUTPUT_PATH, image)
    except:
      print(frame[0])

generateMasks(method="Method of Disks", masksWithMoreThan21Lines="Tracings_Masks_with_more_than_21_lines",
              testImages=30, sweepsOfMoreThan21Lines=False)