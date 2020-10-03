"""Echonet Function Evaluation normalizations of different
volume calculations to assess different shifts against mean"""

def normalizeDict(inputDict):
  zeroItems = inputDict[0]
  zeroItems.sort()
  shift = zeroItems[len(zeroItems)//2]

  for angle in inputDict:
    for i in range(len(inputDict[angle])):
        inputDict[angle][i] -= shift
  return inputDict
