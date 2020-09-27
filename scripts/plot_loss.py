import argparse
import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

model_outputs = "/Users/ishan/echo_index/SmallIndex/output/video/r2plus1d_18_32_2_pretrained"
df = pd.read_csv(os.path.join(model_outputs, "log.csv"))

def latexify():
    """Sets matplotlib params to appear more like LaTeX."""
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
    matplotlib.rcParams.update(params)
