"""Echonet Function Evaluation generation of masks
with lines to determine volume calculation area"""

import pandas as pd
from ast import literal_eval
import os
import cv2
from tqdm import tqdm
from algorithms import funcs as funcs
import loader

def generateMasks(segmentedFramesFolder="Masks_From_VolumeTracing", outputMasksPath="algorithm_masks"):  
  """Function to draw masks on segmented videos to visualize volumetric
    calculation and save them as separate frames in an output directory.
  Args:
      segmentedFramesFolder (str): Folder containing the masks
      outputMasksPath (str): Output directory to save the frames.
  Returns:
      None
  """

  root, _ = loader.dataModules()

  PATH_TO_SEGMENTED_FRAMES_PARENT_DIR = os.path.join(root, segmentedFramesFolder)
  OUTPUT_PATH_TO_MASKS = os.path.join(root, outputMasksPath)
  
  os.makedirs(PATH_TO_SEGMENTED_FRAMES_PARENT_DIR, exist_ok=True) # creates output mask parent directory

  print("\nIterating through each video and making frame if selected")
  for i in tqdm(os.listdir(PATH_TO_SEGMENTED_FRAMES_PARENT_DIR)): # iterates through each row of data frame
    INPUT_FRAME_PATH = os.path.join(PATH_TO_SEGMENTED_FRAMES_PARENT_DIR, i) # (data directory)/frames/(file name)
    OUTPUT_FRAME_PATH = os.path.join(OUTPUT_PATH_TO_MASKS, i) # (data directory)/frames/(file name)

    try:
      ES_volumes, x1, y1, x2, y2 = funcs.calculateVolumeErosionAndDilation(INPUT_FRAME_PATH, 20, iterations=5, method="Method of Disks")
      image = cv2.imread(INPUT_FRAME_PATH) # read in the image from the specified frame path
      for coord in range(len(x1[0])): # iterate through each coordinate
        if coord is 0: # gets the perpendicular/long line
          longLine1stCoords = (x1[0][coord], y1[0][coord])
          longLine2ndCoords = (x2[0][coord], y2[0][coord])
        else: # draws the parallel lines
          cv2.line(image, (x1[0][coord], y1[0][coord]), (x2[0][coord], y2[0][coord]), (25, 102, 215), 1)
        
        cv2.line(image, longLine1stCoords, longLine2ndCoords, (31, 55, 145), 2) # Drawing the perpendicular/long line in different color
        cv2.imwrite(OUTPUT_FRAME_PATH, image)
    except:
      print(i + " was not able to be calculated")

generateMasks()