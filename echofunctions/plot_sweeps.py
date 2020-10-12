"""Echonet Function Evaluation plotting
the timing sweeps to visualize beats"""



# Plot sizes (from Echonet segmentation.py)
fig = plt.figure(figsize=(size.shape[0] / 50 * 1.5, 3))
plt.scatter(np.arange(size.shape[0]) / 50, size, s=1)
ylim = plt.ylim()
for s in systole:
plt.plot(np.array([s, s]) / 50, ylim, linewidth=1)
plt.ylim(ylim)
plt.title(os.path.splitext(filename)[0])
plt.xlabel("Seconds")
plt.ylabel("Size (pixels)")
plt.tight_layout()
plt.savefig(os.path.join(output, "size", os.path.splitext(filename)[0] + ".pdf"))
plt.close(fig)