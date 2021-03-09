"""Calculates volumes from human tracings' coordinates"""

def calcParallelAndMaxPoints(x1, y1, x2, y2):
  slopes, lowerInterceptAveragePoints, higherInterceptAveragePoints = [], [], []
  k = 0
  for i in range(len(x1)):
    slope = getSlope([x1[i], y1[i]], [x2[i], y2[i]])
    slopes.append(slope)
  
  maxIndex = differenceInSign(slopes)
  maxX1 = x1[maxIndex]
  maxY1 = y1[maxIndex]
  maxX2 = x2[maxIndex]
  maxY2 = y2[maxIndex]

  for i in range(len(x1)):
    if i is not maxIndex:
      lowerInterceptAveragePoints.append([])
      higherInterceptAveragePoints.append([])

      lowerInterceptAveragePoints[k] = [x1[k], y1[k]]
      higherInterceptAveragePoints[k] = [x2[k], y2[k]]
      k += 1

  return maxX1, maxY1, maxX2, maxY2, lowerInterceptAveragePoints, higherInterceptAveragePoints

def getSlope(point1, point2):
  if ((point1[0] == point2[0])):
    return 0
  return (point1[1] - point2[1])/(point1[0] - point2[0])

def differenceInSign(slopes):
  negativeSlopes, positiveSlopes = [], []
  for i in range(len(slopes)):
    if i < 0:
      negativeSlopes.append(i)
    else:
      positiveSlopes.append(i)
    
  if len(negativeSlopes) is 1:
    maxIndex = negativeSlopes[0]
  else:
    maxIndex = positiveSlopes[0]
    
  return maxIndex