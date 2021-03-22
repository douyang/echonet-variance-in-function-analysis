# """Create CSV for timing data (true frame and predicted frames)"""

# import pandas as pd
# import os
# import config
# import loader
# from algorithms import funcs as funcs
# import collections
# import cv2
# from ast import literal_eval
# from tqdm import tqdm
# import find_peaks

# # Returns dictionary with predicted frames
# def gatherTimingPredictions(inputFolder="Control-Videos-Segmented", outputFolder="control_video_frames", CSVName="Frame Timing Predictions.csv",
#                             createFrames=False):
#   """Function to predict end-systolic and end-diastolic timings for each video
#   Args:
#       inputFolder (str): Folder containing the segmented videos
#       outputFolder (str): Output directory to save all frames of each video.
#       CSVName (str): Name of the CSV file to export
#       createFrames (bool): Determines whether to create frames for each video or not
#   Returns:
#       None
#   """

#   root=config.CONFIG.DATA_DIR
#   videoPath = os.path.join(root, inputFolder)
  
#   dataList = []
#   fails, video_count = 0, 0

#   for videoName in tqdm(os.listdir(videoPath)):
#     if "avi" in videoName:
#       video_count += 1
#       ES_frame, ED_frame = find_peaks.returnPeaks(videoName=os.path.splitext(videoName)[0],
#                                         inputFolderName=inputFolder, outputFolderName=outputFolder, makeFrames=createFrames)
        
#       #ES_frame, ED_frame = prediction_frames[0], prediction_frames[1] # predicted timings
#       #true_ES_frame, true_ED_frame = true_frames[0], true_frames[1] # true timings

#       videoData = {"Video Name": videoName, "Predicted ESV": ES_frame, "Predicted EDV": ED_frame}
#                   #"True ESV": true_ES_frame, "True EDV": true_ED_frame}
        
#       dataList.append(videoData) # add the sub-dictionaries (each video)
    
#   df = pd.DataFrame(dataList) # convert to dataframe
#   export_path = os.path.join(root, CSVName) # path to export

#   df.to_csv(export_path) # export to CSV
#   print(fails)
#   print(video_count)

# gatherTimingPredictions()

import pandas as pd
from ast import literal_eval
import os
import cv2
from tqdm import tqdm
from algorithms import funcs as funcs
import loader
from PIL import Image 
import skimage.draw
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


x = "/Users/ishan/Documents/Stanford/EchoData/control_video_frames/122.jpg"
vidPath = "/Users/ishan/Documents/Stanford/EchoData/Control-Videos-Segmented/Control_0027_0001.avi"
volumes, x1, y1, x2, y2, d = funcs.calculateVolumeAngleShift(x, 20, 10, method="Method of Disks")

video = loader.loadvideo(vidPath).astype(np.float32)
for iteration in x1:
    mask = loader.READ_AND_CROP_FRAME(vidPath, 122, False)
    overlay = mask.copy() # overlay layer

    x = np.concatenate((x1[iteration][1:], np.flip(x2[iteration][1:])))
    y = np.concatenate((y1[iteration][1:], np.flip(y2[iteration][1:])))

    x0 = np.concatenate((x1[0][1:], np.flip(x2[0][1:])))
    y0 = np.concatenate((y1[0][1:], np.flip(y2[0][1:])))

    r, c = skimage.draw.polygon(np.rint(y).astype(np.int), np.rint(x).astype(np.int), (video.shape[2], video.shape[3]))
    r0, c0 = skimage.draw.polygon(np.rint(y0).astype(np.int), np.rint(x0).astype(np.int), (video.shape[2], video.shape[3]))
    #mask = np.zeros((video.shape[2], video.shape[3]), np.float32)

    overlay[r, c] = (134, 34, 35)
    #mask[r0, c0] = (24, 234, 255)

    rescaled = (255.0 / mask.max() * (mask - mask.min())).astype(np.uint8)

    im = Image.fromarray(mask)
    #if iteration > 0:
    image_new = cv2.addWeighted(overlay, 0.8, np.array(im), 0.8, 0)

    image_new = Image.fromarray(np.uint8(image_new)).convert('RGB')
    image_new.save(str(iteration) + ".png")