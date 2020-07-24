import matplotlib.pyplot as plt
import random
import PIL
import math
import cv2
import numpy as np
from PIL import Image
import os


def captureFrames(dataPath, vid):
    videoPath = dataPath + "/videos/" + vid

    cap = cv2.VideoCapture(videoPath)
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break

        framePath = dataPath + '/frames/original/' + vid

        # Make dir if capture dir not available
        if os.path.isdir(framePath) is False:
            os.mkdir(framePath)

        frameOutput = framePath + '/frame'+ str(i)+ '.png'
        
        cv2.imwrite(frameOutput, frame)
        
        print(frameOutput)
        i+=1
    
    cap.release()
    cv2.destroyAllWindows()

def cropFrame(dataPath, imagePath, vid, name):

    image = imagePath

    image = cv2.imread(image)
    h, w, c = image.shape

    # Starting Coords
    x1 = 0
    y1 = 0

    # Ending Coords
    x2 = round(w/2)
    y2 = h

    # Crop
    crop = image[y1:y2, x1:x2]

    # Save Image
    cropDir = dataPath + '/frames/crop/'
    cropPath = dataPath + '/frames/crop/' + vid

    # Makes overall crop dir
    if os.path.isdir(cropDir) is False:
        os.mkdir(cropDir)

    # Makes dir for each video
    if os.path.isdir(cropPath) is False:
        os.mkdir(cropPath)

    cv2.imwrite(cropPath + "/" + name, crop)

    cv2.destroyAllWindows()


dataPath = "/Users/ishan/Documents/Stanford/ouyang-data"

if os.path.isdir(dataPath + "/frames") is False:
    os.mkdir(dataPath + "/frames")

if os.path.isdir(dataPath + "/frames/crop") is False:
    os.mkdir(dataPath + "/frames/crop")

if os.path.isdir(dataPath + "/frames/original") is False:
    os.mkdir(dataPath + "/frames/original")


# # Uncomment these to generate all frames from all videos
# for vid in os.listdir(dataPath + "/videos"):
#     if vid[-3:] == "avi":
#         captureFrames(dataPath, vid)

capturedFramesPath = dataPath + "/frames/original/"

# Uncomment these to generate crops of all frames
for vid in os.listdir(capturedFramesPath):
    if vid[-3:] == "avi":
        vidPath = capturedFramesPath + vid
        for frame in os.listdir(vidPath):
            
            # Save crop to given filepath
            imagePath = vidPath + "/" + frame
            cropFrame(dataPath, imagePath, vid, frame)