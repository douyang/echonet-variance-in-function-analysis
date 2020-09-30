import os, os.path
from os.path import splitext
import numpy as np
import sys
import matplotlib.pyplot as plt
import torch
import torchvision
import wget
import sys
from PIL import Image
import funcs
import config
import cv2

root = config.CONFIG.DATA_DIR

destination_folder = os.path.join(root, "output")
destination_for_weights = os.path.join(root, "weights")

if os.path.exists(destination_for_weights):
    print("The weights are at", destination_for_weights)
else:
    print("Creating folder at ", destination_for_weights, " to store weights")
    os.mkdir(destination_for_weights)
    
segmentationWeightsURL = 'https://github.com/douyang/EchoNetDynamic/releases/download/v1.0.0/deeplabv3_resnet50_random.pt'

if not os.path.exists(os.path.join(destination_for_weights, os.path.basename(segmentationWeightsURL))):
    print("Downloading Segmentation Weights, ", segmentationWeightsURL," to ",os.path.join(destination_for_weights, os.path.basename(segmentationWeightsURL)))
    filename = wget.download(segmentationWeightsURL, out = destination_for_weights)
else:
    print("Segmentation Weights already present")

torch.cuda.empty_cache()

def collate_fn(x):
    x, f = zip(*x)
    i = list(map(lambda t: t.shape[1], x))
    x = torch.as_tensor(np.swapaxes(np.concatenate(x, 1), 0, 1))
    return x, f, i

model = torchvision.models.segmentation.deeplabv3_resnet50(pretrained=False, aux_loss=False)
model.classifier[-1] = torch.nn.Conv2d(model.classifier[-1].in_channels, 1, kernel_size=model.classifier[-1].kernel_size)

print("loading weights from ", os.path.join(destination_for_weights, "deeplabv3_resnet50_random"))

if torch.cuda.is_available():
    print("cuda is available, original weights")
    device = torch.device("cuda")
    model = torch.nn.DataParallel(model)
    model.to(device)
    checkpoint = torch.load(os.path.join(destination_for_weights, os.path.basename(segmentationWeightsURL)))
    model.load_state_dict(checkpoint['state_dict'])
else:
    print("cuda is not available, cpu weights")
    device = torch.device("cpu")
    checkpoint = torch.load(os.path.join(destination_for_weights, os.path.basename(segmentationWeightsURL)), map_location = "cpu")
    state_dict_cpu = {k[7:]: v for (k, v) in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict_cpu)

model.eval()

def segment(inp):
    x = inp.transpose([2, 0, 1])  #  channels-first
    x = np.expand_dims(x, axis=0)  # adding a batch dimension    
    
    mean = x.mean(axis=(0, 2, 3))
    std = x.std(axis=(0, 2, 3))
    x = x - mean.reshape(1, 3, 1, 1)
    x = x / std.reshape(1, 3, 1, 1)
    
    with torch.no_grad():
        x = torch.from_numpy(x).type('torch.FloatTensor').to(device)
        output = model(x)    
    
    y = output['out'].numpy()
    y = y.squeeze()
    
    out = y>0    
    
    mask = inp.copy()
    mask[out] = np.array([0, 0, 255])
    
    #return mask
    rescaled = (255.0 / mask.max() * (mask - mask.min())).astype(np.uint8)

    im = Image.fromarray(rescaled)
    imagePath = os.path.join("testing", "segmented_img.png")
    im.save(imagePath)

    volumes, x1, y1, x2, y2, degrees = funcs.calculateVolume(imagePath, 20, 1, "Method of Disks")
    image = cv2.imread(imagePath) # read in the image from the specified frame path
    
    for coord in range(len(x1[0])): # iterate through each coordinate
      if coord is 0: # gets the perpendicular/long line
        longLine1stCoords = (x1[0][coord], y1[0][coord])
        longLine2ndCoords = (x2[0][coord], y2[0][coord])
      else:
        cv2.line(image, (x1[0][coord], y1[0][coord]), (x2[0][coord], y2[0][coord]), (255, 255, 255), 1)
        
    cv2.line(image, longLine1stCoords, longLine2ndCoords, (255, 255, 255), 1) # Drawing the perpendicular/long line in different color

    return image

import gradio as gr

i = gr.inputs.Image(shape=(112, 112))
o = gr.outputs.Image()

examples = [["testing/img1.jpg"], ["testing/img2.jpg"]]
title = "Cardiac Function Evaluation"
description = "Accurate assessment of ventricular vol-umes  and  cardiac  function  is  essentialfor  diagnosis  and  treatment  of  cardio-vascular  disease,   however  the  assess-ment  has  many  dependencies,  unreli-able assumptions in algorithm calcula-tion, and variability in accurate humanassessment.   We  developed  an  end-to-end  deep  learning  model  for  evaluat-ing  cardiac  function  by  1)  automatedidentification  of  end-systole  and  end-diastole, 2) segmentation of the left ven-tricle, and 3) algorithmic evaluation ofthe  cardiac  function.    Using  a  video-based deep learning model, end systolewas accurately identified an average ofwithin  150  ms  from  the  human  labelsand  end  diastole  was  accurately  iden-tified an average of within 167 ms fromthe human labels.  From the determinedframes, ventricular volumes were calcu-lated.  Even with the same ventriculartracing, slight perturbations in long axisposition resulted in variance in the esti-mates of ventricular volume up to 8.0%for  end  systole  and  5.2%  for  end  dias-tole.  Using standard volumetric formu-las, the ultimate calculated LVEF var-ied up to 5.8%.  Even with precise iden-tification of cardiac times and segmen-tation of cardiac structures, small varia-tions can compound to significantly im-pact eventual evaluations of ventricularfunction,  suggesting  limitations  in  theprecision of deep learning models for as-sessing cardiac function"
thumbnail = "https://raw.githubusercontent.com/gradio-app/hub-echonet/master/thumbnail.png"

gr.Interface(segment, i, o, examples=examples, allow_flagging=False,
	title=title, description=description, thumbnail=thumbnail).launch()