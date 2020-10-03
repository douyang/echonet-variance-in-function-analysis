import matplotlib.pyplot as plt
import numpy as np
import os

def show_images(images, cols = 1, titles = None):
    """Display a list of images in a single figure with matplotlib.
    
    Parameters
    ---------
    images: List of np.arrays compatible with plt.imshow.
    
    cols (Default = 1): Number of columns in figure (number of rows is 
                        set to np.ceil(n_images/float(cols))).
    
    titles: List of titles corresponding to each image. Must have
            the same length as titles.
    """
    params = {'axes.titlesize': 8,
            'axes.labelsize': 8,
            'font.size': 8,
            'legend.fontsize': 8,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'font.family': 'DejaVu Serif',
            'font.serif': 'Computer Modern',
            }
    plt.rcParams.update(params)
    assert((titles is None)or (len(images) == len(titles)))
    n_images = len(images)
    if titles is None: titles = ['Image (%d)' % i for i in range(1,n_images + 1)]
    fig = plt.figure()
    plt.title("Point Shift Sweeps from -30 to 30")
   
    for n, (image, title) in enumerate(zip(images, titles)):
        
        a = fig.add_subplot(cols, np.ceil(n_images/float(cols)), n + 1)
        a.get_yaxis().set_visible(False)
        a.get_xaxis().set_visible(False)

        if image.ndim == 2:
            plt.gray()
        plt.imshow(image, origin='lower') 
    fig.set_size_inches(np.array(fig.get_size_inches()))
    

    plt.show()


import cv2
import glob
import numpy as np

X_data = []
files = glob.glob ("/Users/ishan/Documents/Stanford/echonet-function-evaluation/testing/samples/*.png")
for myFile in files:
    print(myFile)
    image = cv2.imread (myFile)
    im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    X_data.append (im_rgb[::-1])

titles = ["Original Video", "Segmented Frame", "Method of Disks", "Total"]
print('X_data shape:', np.array(X_data).shape)

show_images(np.array(X_data), titles=titles)