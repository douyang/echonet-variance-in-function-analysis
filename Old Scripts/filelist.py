import pandas as pd
import numpy as np

dataPath = "/Users/ishan/Documents/Stanford/ouyang-data/"

df = pd.read_csv (dataPath + 'volume.csv')

filelist_csv = []

t = df.iterrows()
for (i, row1), (j, row2) in zip(t, t):
    filename = row1["FileName"]
    
    EDV = row1["Volume"]
    ESV = row2["Volume"]
    EDVframe = int(row1["Frame"])
    ESVframe = int(row2["Frame"])

    try:
        ESV = float(ESV)
        EDV = float(EDV)
        if ESV > EDV:
            EDV, ESV = ESV, EDV
            EDVframe, ESVframe = EDVframe, ESVframe
            
        EF = (float(EDV)-float(ESV))/float(EDV)
        filelist_csv.append([filename, EF*100, ESV, EDV, EDVframe, ESVframe, ""])
        if EF > 1:
            print(filename, EF*100, ESV, EDV, EDVframe, ESVframe, "")
    except:
        filelist_csv.append([filename, "Couldn't calculate", ESV, EDV, EDVframe, ESVframe, ""])

#Create and export dataframe to CSV
new_df = pd.DataFrame(filelist_csv)
new_df.columns = ['FileName', 'EF', 'ESV', 'EDV', "EDV-Frame", "ESV-Frame", "Negative EF?"]
new_df.to_csv(dataPath + 'filelist.csv')