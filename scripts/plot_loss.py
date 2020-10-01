#!/usr/bin/env python3

import argparse
import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

small_index_csv = "/Users/ishan/Documents/Stanford/EchoData/output/test_normalizedsmallindex.csv"
large_index_csv = "/Users/ishan/Documents/Stanford/EchoData/output/test_normalizedlargeindex.csv"

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
plt.rcParams.update(params)

data = pd.read_csv(large_index_csv, sep=',',header=None)
data = data.iloc[:, 0]

data.plot(kind='hist')

plt.ylabel('Frequency')
plt.xlabel('Difference in Index Prediction')

plt.title('Difference in LargeIndex Model Prediction vs. Ground Truth')
plt.show()