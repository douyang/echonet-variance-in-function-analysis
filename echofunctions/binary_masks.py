"""Making binary masks from 
coordinates given in VolumeTracings.csv"""

import pathlib
import os
import collections
from PIL import Image
import cv2
import numpy as np
import skimage.draw
import torch.utils.data
import loader
from functools import reduce
import operator
import math
import tqdm

# Capture and Make Frames + Crop
def initVars(method="Method of Disks"):
  trace = collections.defaultdict(_defaultdict_of_lists)
  frames = collections.defaultdict(list)

  fnames = []

  root, _ = loader.dataModules()

  with open(os.path.join(root, "FileList.csv")) as f:
    header = f.readline().strip().split(",")
    filenameIndex = header.index("FileName")

    for line in f:
      lineSplit = line.strip().split(',')
      fileName = lineSplit[filenameIndex]

      if os.path.exists(os.path.join(root, "Videos", fileName)):
        fnames.append(fileName)

  with open(os.path.join(root, "VolumeTracings.csv")) as f:
    header = f.readline().strip().split(",")
    assert header == ["FileName", "X1", "Y1", "X2", "Y2", "Frame"]

    for line in f:
      filename, x1, y1, x2, y2, frame = line.strip().split(',')
      x1 = float(x1)
      y1 = float(y1)
      x2 = float(x2)
      y2 = float(y2)
      frame = int(frame)
      if frame not in trace[filename]:
        frames[filename].append(frame)
      trace[filename][frame].append((x1, y1, x2, y2))

  for filename in frames:
    for frame in frames[filename]:
      trace[filename][frame] = np.array(trace[filename][frame])
  
  return trace, fnames, frames, root

def createTruthMasks(outputFolderName="Masks_From_VolumeTracing", moreLinesFolderName="Tracings_Masks_with_more_than_21_lines", plainLinesFolderName="Blank_Image_Ground_lines_from_Tracings"):
  trace, fnames, frames, root = initVars()

  print(trace)

  for index in fnames:
    for frame_index in [0, -1]:
      video = os.path.join(root, "Videos", index)
      video = loader.loadvideo(video).astype(np.float32)
      
      t = trace[index][frames[index][frame_index]]

      x1, y1, x2, y2 = t[:, 0], t[:, 1], t[:, 2], t[:, 3]
      x = np.concatenate((x1[1:], np.flip(x2[1:])))
      y = np.concatenate((y1[1:], np.flip(y2[1:])))

      r, c = skimage.draw.polygon(np.rint(y).astype(np.int), np.rint(x).astype(np.int), (video.shape[2], video.shape[3]))
      mask = np.zeros((video.shape[2], video.shape[3]), np.float32)
      mask[r, c] = 1

      if len(t) < 22:
        os.makedirs(os.path.join(root, outputFolderName), exist_ok=True) # creates frames parent directory
        rescaled = (255.0 / mask.max() * (mask - mask.min())).astype(np.uint8)

        im = Image.fromarray(rescaled)
        im.save(os.path.join(root, outputFolderName, index + "_" + str(frames[index][frame_index]) + '.png'))
      else: # more than 21 lines
        os.makedirs(os.path.join(root, moreLinesFolderName), exist_ok=True) # creates frames parent directory
        os.makedirs(os.path.join(root, plainLinesFolderName), exist_ok=True) # creates frames parent directory

        rescaled = (255.0 / mask.max() * (mask - mask.min())).astype(np.uint8)

        im = Image.fromarray(rescaled)
        im.save(os.path.join(root, moreLinesFolderName, index + "_" + str(frames[index][frame_index]) + '.png'))

        # Draw lines on black image
        blank_image = np.zeros((126, 126, 3), dtype="uint8")
        for coord in range(len(x1)):
          cv2.line(blank_image, (int(x1[coord]), int(y1[coord])), (int(x2[coord]), int(y2[coord])), (255, 255, 255), 1)

        cv2.imwrite(os.path.join(root, plainLinesFolderName, index + "_" + str(frames[index][frame_index]) + '.png'), blank_image)

def _defaultdict_of_lists():
    """Returns a defaultdict of lists.
    This is used to avoid issues with Windows (if this function is anonymous,
    the Echo dataset cannot be used in a dataloader).
    """

    return collections.defaultdict(list)

createTruthMasks(outputFolderName="Masks_From_VolumeTracing")