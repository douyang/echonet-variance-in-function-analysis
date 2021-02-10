"""Echonet Function Evaluation segmentation predictions
using pre-trained weights from Echonet release"""

import os, os.path
from os.path import splitext
import numpy as np
from PIL import Image
import sys
import matplotlib.pyplot as plt
import torch
import torchvision
import wget
import config

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
  
  return mask