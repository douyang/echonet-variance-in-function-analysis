differenceInVolumes = {(0, 5): 11, (0, 0): 10, (-5, 0): 6}
differenceInVolumes = list(differenceInVolumes.items())
differenceInVolumes.sort(key=lambda volumeShift: volumeShift[0][0] + volumeShift[0][1])

# setting x-tick labels
labels = [str(volumeShift[0]) for volumeShift in differenceInVolumes]
data = [volumeShift[1] for volumeShift in differenceInVolumes]

print(labels)
print(data)