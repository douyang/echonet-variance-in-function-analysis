differenceInVolumes = {(-90, -85): 10, (-100, -95): 11, (0, 5): 6}
differenceInVolumes = list(differenceInVolumes.items())
differenceInVolumes.sort(key=lambda volumeShift: volumeShift[0][0])

# setting x-tick labels
labels = [str(volumeShift[0]) for volumeShift in differenceInVolumes]
data = [volumeShift[1] for volumeShift in differenceInVolumes]

print(labels)
print(data)