## EchoNet Function Evaluation:<br/>Quantifying Model Variation in Assessing Cardiac Function

An automated end-to-end pipeline for  
1) assessing cardiac function
2) quantifying error in left ventricular ejection fraction calculation with slight clinical perturbations


## Examples
We show examples of our different systematic variation of cardiac function assessment. The error opportunities showcased are over/under tracing of the left ventricle, rotations of main longitudinal axis, foreshortened apex and mitral valve annulus level foreshortening. No human tracings for these patients were used.

| Normal Tracing | Over/Under Tracing | Angle Rotations | Main Axis Foreshortening |
|---------------------------------| ----------------------------------   | -------------------------------- | ------------------------------ |
| ![](docs/media/Normal.png) | ![](docs/media/Overtrace.png) | ![](docs/media/PositiveAngle.png) | ![](docs/media/Top.png) |
|                                              | ![](docs/media/Undertrace.png) | ![](docs/media/NegativeAngle.png) | ![](docs/media/Bottom.png) |


## Installation
First, clone this repository and enter the directory by running:
```
git clone https://github.com/douyang/echonet-function-evaluation
cd echonet-function-evaluation
```

EchoNet-Function-Evaluation is implemented for Python 3, and depends on the following packages:
* NumPy
* Matplotlib
* Pandas
* OpenCV
* Pillow
* SciPy
* tqdm

The dependencies can be installed by navigating to the cloned directory and running:
```
pip install --user .
```

## Usage
### Setting Path to Data
By default, the pipeline assumes that a copy of the data is saved in a folder named ```EchoData/``` in this directory. This path can be changed by setting an absolute path in the file named ```data.cfg``` (an example is given in the file already).

### Running Code
In order to fully utilize the evaluation pipeline, it is essential to create the necessary frames from the segmented videos generated from Echonet. To adequately perform such a task, we have a ```mask.py``` script. The script locates all of the videos from the data repository, and it creates the necessary frames from ```VolumeTracings.csv```.

#### Capturing and Creating Frames
```
cmd="import echofunctions; echofunctions.mask.generateMasks(method=\"Simpson\",
                                                      createRawFrames=True)"
python3 -c "${cmd}"
```

This creates two directories named ```frames/``` and ```masks/```, which will contain the raw frames and the masked images from the pipeline, respectively.

#### Calculated Timing against Ground Truth
```
cmd="import echofunctions; echofunctions.timings_against_ground.compareVolumePlot(method=\"Simpson\",
                                                                                    timing="EF")"
python3 -c "${cmd}"
```
This will open and display a plot that will show a scatter plot comparison of the calculated selected timing against ground truth for a given selected method of choice. One can save the plot to their local directory or experiment with matplotlib's GUI.

#### Calculated Method Against Method
```
cmd="import echofunctions; echofunctions.method_against_method.compareVolumePlot(method1=\"Simpson\", method2=\"Biplane Area\",
                                                                                 timing="EF")"
python3 -c "${cmd}"
```
This will open and display a plot that will show a scatter plot comparison of the calculated selected timing using the first method against the second method for a given selected timing of choice. One can save the plot to their local directory or experiment with matplotlib's GUI.
