import pandas as pd

smallIndexDf = pd.read_csv('./data/test_normalizedsmallindex.csv')
largeIndexDf = pd.read_csv('./data/test_normalizedlargeindex.csv')

print(smallIndexDf.head(10))
print(largeIndexDf.head(10))

print(smallIndexDf.std(axis = 0, skipna = True))
print(largeIndexDf.std(axis = 0, skipna = True)) 
