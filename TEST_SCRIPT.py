import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Data for MaximalRectangle1
rectangles = [
    {"width": 92.0, "height": 42.0, "x": 0, "y":0},
    {"width": 25.0, "height": 67.0, "x": 92.0, "y":0},
    {"width": 24.0, "height": 25.0, "x": 0, 'y': 42.0},
    {"width": 4.0, "height": 24.0, "x": 117.0, 'y': 0},
    {"width": 4.0, "height": 67.0, "x": 121.0, 'y': 0},
    {"width": 4.0, "height": 47.875, "x": 125.0, 'y': 0},
    {"width": 43.0, "height": 22.0, "x": 24.0, 'y': 42.0},
    {"width": 4.0, "height": 43.0, "x": 129.0, 'y': 0},
    {"width": 4.0, "height": 21.125, "x": 133.0, 'y': 0},
]

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 138)
ax.set_ylim(0, 78)
ax.set_title('MaximalRectangle1 Placements')

# Plot each rectangle
for rect in rectangles:
    patch = patches.Rectangle((rect['x'], rect['y']), rect['width'], rect['height'], linewidth=1, edgecolor='b', facecolor='blue', alpha=0.5)
    ax.add_patch(patch)

# Set aspect of the plot to be equal
ax.set_aspect('equal', adjustable='box')

# Save plot to a file instead of showing it
plt.savefig('/media/vaibhav/5C60D97E60D95F78/marble cutting/2d_packing/rectangle_plot2.png')