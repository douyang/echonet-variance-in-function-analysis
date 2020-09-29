# differenceInVolumes = {(0, 5): 11, (0, 0): 10, (-5, 0): 6}
# differenceInVolumes = list(differenceInVolumes.items())
# differenceInVolumes.sort(key=lambda volumeShift: volumeShift[0][0] + volumeShift[0][1])

# # setting x-tick labels
# labels = [str(volumeShift[0]) for volumeShift in differenceInVolumes]
# data = [volumeShift[1] for volumeShift in differenceInVolumes]

# print(labels)
# print(data)


arr = [[2,4, 5, 5,6,6,7, 9]]
arr = [[shift - 2 for shift in arr[0]]]
print(arr)
