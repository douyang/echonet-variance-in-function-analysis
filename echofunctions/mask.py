"""Echonet Function Evaluation generation of masks
with lines to determine volume calculation area"""

import pandas as pd
from ast import literal_eval
import os
import cv2

from algorithms import funcs as funcs
import loader

def capture(method, createRawFrames, imageType):

  PATH_DATA = [] # list that contains path information (later used for masks)
  root, df = loader.dataModules()
  segmented_echo_data = os.path.join(root, "Videos")

  PATH_TO_RAW_FRAMES_PARENT_DIR = os.path.join(root, "Masks_From_VolumeTracing")
  PATH_TO_MASK_FRAMES_PARENT_DIR = os.path.join(root, "Masks_From_VolmeTracing_And_Lines_From_Algorithm")
  
  os.makedirs(PATH_TO_RAW_FRAMES_PARENT_DIR, exist_ok=True) # creates frames parent directory
  os.makedirs(PATH_TO_MASK_FRAMES_PARENT_DIR, exist_ok=True) # creates mask parent directory

  for i in range(len(df)): # iterates through each row of data frame
    videoName = df.iloc[i, 0] # name of video
    frameNumber = df.iloc[i, 1] # timing for clip

    videoPath = os.path.join(segmented_echo_data, videoName + ".avi") # path to each video
    if (os.path.exists(videoPath)):
      OUTPUT_FRAME_NAME = videoName + "_" + str(frameNumber) + "." + imageType # concatenate video name with frame number as file name
      OUTPUT_FRAME_PATH = os.path.join(PATH_TO_RAW_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME) # (data directory)/frames/(file name)
      
      if createRawFrames is True:
        crop = loader.READ_AND_CROP_FRAME(videoPath, frameNumber)
        cv2.imwrite(OUTPUT_FRAME_PATH, crop)
        # segmented_img = loader.SEGMENT_FRAME(videoPath, frameNumber)
        # cv2.imwrite(OUTPUT_FRAME_PATH, segmented_img)

      PATH_DATA.append([OUTPUT_FRAME_PATH, 20, PATH_TO_MASK_FRAMES_PARENT_DIR, OUTPUT_FRAME_NAME])

  return PATH_DATA

def generateMasks(method="Method of Disks", createRawFrames=False, imageType="png"):
  PATH_DATA = capture(method, createRawFrames, imageType)

  for frame in PATH_DATA:
    PATH_TO_RAW_FRAME = frame[0] # path to the raw frame
    numberOfParallelLines = frame[1] # number of parallel lines in mask
    MASK_OUTPUT_PATH = os.path.join(frame[2], frame[3]) # join parent path (root) with mask output name
    if os.path.exists(PATH_TO_RAW_FRAME):
      try:
        volumes, x1, y1, x2, y2, degrees = funcs.calculateVolume(PATH_TO_RAW_FRAME, numberOfParallelLines, method)
        image = cv2.imread(PATH_TO_RAW_FRAME) # read in the image from the specified frame path
        for coord in range(len(x1[0])): # iterate through each coordinate
          if coord is 0: # gets the perpendicular/long line
            longLine1stCoords = (x1[0][coord], y1[0][coord])
            longLine2ndCoords = (x2[0][coord], y2[0][coord])
          else: # draws the parallel lines
            cv2.line(image, (x1[0][coord], y1[0][coord]), (x2[0][coord], y2[0][coord]), (25, 102, 215), 1)
          
          cv2.line(image, longLine1stCoords, longLine2ndCoords, (31, 55, 145), 2) # Drawing the perpendicular/long line in different color

          cv2.imwrite(MASK_OUTPUT_PATH, image)
      except:
        print(PATH_TO_RAW_FRAME)

generateMasks(imageType="png", createRawFrames=True)