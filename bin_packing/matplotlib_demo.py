import matplotlib.pyplot as plt
import matplotlib.patches as patches
import greedypacker as g
import csv
import os
from pathlib import Path


def plot_graph(rectangles, num, algo, heuristic):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 138)
    ax.set_ylim(0, 78)
    ax.set_title(f'Graph: {num}')
    ax.set_xlabel("Width")
    ax.set_ylabel("Height")
    ax.set_aspect('equal', adjustable='box')

    ax.autoscale(enable=False)

    ax.set_xticks([i for i in range(0, 139, 20)] + [138])
    ax.set_yticks([i for i in range(0, 79, 10)] + [78])

    margin = 1

    # Plot each rectangle
    for rect in rectangles:
        patch = patches.Rectangle((rect['x'], rect['y']), rect['width'], rect['height'], linewidth=1, edgecolor='b', facecolor='blue', alpha=0.5)
        ax.add_patch(patch)

        # Annotate width inside the rectangle with margin
        ax.text(rect['x'] + rect['width']/2, rect['y'] + margin, f"{rect['width']}",
                verticalalignment='bottom', horizontalalignment='center',
                fontsize=8, color='black', weight='bold')

        # Annotate height inside the rectangle with margin
        ax.text(rect['x'] + margin, rect['y'] + rect['height']/2, f"{rect['height']}",
                verticalalignment='center', horizontalalignment='left',
                fontsize=8, color='black', weight='bold', rotation=90)


    # Check if the directory exists, create if not
    BASE_DIR = Path(__file__).resolve().parent.parent
    directory_path = f'{BASE_DIR}/media/{algo}/{heuristic}/'

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Save plot to a file instead of showing it
    image_name = f"image_{num}.png"
    plt.savefig(directory_path + image_name)

    # Close the figure to free memory
    plt.close(fig)


if __name__ == '__main__':
    algorithms = {
        'maximal_rectangle': ['best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside', 'bottom_left', 'contact_point'],
        # 'guillotine': ['best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside'],
        # 'skyline': ['bottom_left', 'best_fit']
    }

    for algo in algorithms:
        for heuristic in algorithms[algo]:
            M = g.BinManager(138,78, pack_algo=algo, heuristic=heuristic, rotation=True, sorting=True, wastemap=True)
            
            demoList = []    
            total_tiles = 0
            BASE_DIR = Path(__file__).resolve().parent.parent
            filepath = f'{BASE_DIR}/static/csv/tiles_data_4.csv'

            with open(filepath, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    height = float(row['height'])
                    width = float(row['width'])
                    quantity = row['quantity']
                    total_tiles += int(quantity)
                    
                    for _ in range(int(quantity)):
                        demoList.append(g.Item(height, width))
            
            M.add_items(*demoList)
            M.execute()

            # print(f"Algo: {algo}, Heuristic: {heuristic}, Total Tiles: {total_tiles}, Bins: {len(M.bins)}")
            print(f"Algo: {algo}, Heuristic: {heuristic}, Total Tiles: {total_tiles}")

            plots = []
            area_occupied = 0
            total_area = 0
            for bin in M.bins:
                plotList = []
                for item in bin.items:
                    plotList.append({"width": item.width, "height": item.height, "x": item.x, "y":item.y})
                    area_occupied += item.area
                plots.append(plotList)
                total_area += (138*78)
            
            percentage_occupied = (area_occupied / total_area) * 100
            percentage_wasted = 100 - percentage_occupied
            print(f"Area Occupied: {area_occupied}, Total Area: {total_area}, Percentage Occupied: {round(percentage_occupied, 3)}%, Percentage Wasted: {round(percentage_wasted, 3)}%")

            count = 0
            for plot in plots:
                plot_graph(plot, count, algo, heuristic)
                count += 1



# *** ACTUAL ANSWERS ***
# Tile Data 1: 131
# Tile Data 2: 63
# Tile Data 3: 42
# Tile Data 4: 10
# Tile Data 5: 54
# Tile Data 6: 72
# Tile Data 7: 14
# Tile Data 8: 98