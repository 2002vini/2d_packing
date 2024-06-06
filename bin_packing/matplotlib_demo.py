import matplotlib.pyplot as plt
import matplotlib.patches as patches
import greedypacker as g
import csv
import os
from pathlib import Path

SLAB_LENGTH = 138
SLAB_WIDTH = 78


def plot_graph(slab_data, num, algo, heuristic, total_bins_used):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, SLAB_LENGTH)
    ax.set_ylim(0, SLAB_WIDTH)
    ax.set_title(f'Graph: {num}/{total_bins_used}')
    ax.set_xlabel("Width")
    ax.set_ylabel("Length")
    ax.set_aspect('equal', adjustable='box')

    ax.autoscale(enable=False)

    ax.set_xticks([i for i in range(0, SLAB_LENGTH+1, 20)] + [SLAB_LENGTH])
    ax.set_yticks([i for i in range(0, SLAB_WIDTH+1, 10)] + [SLAB_WIDTH])

    margin = 1

    # Plot each rectangle
    for rect in slab_data['rectangles']:
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

    # Display additional statistics
    stats_text = f"Total bins used: {total_bins_used}\nArea occupied: {slab_data['slab_percentage_occupied']}%\nArea wasted: {slab_data['slab_percentage_wasted']}%"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    fig.text(0.5, 0.07, stats_text, ha='center', va='bottom', fontsize=10, bbox=props)
    fig.subplots_adjust(bottom=0.2)  # Increase the bottom margin

    # Check if the directory exists, create if not and save the image
    ROOT_DIR = Path(__file__).resolve().parent.parent
    directory_path = f'{ROOT_DIR}/media/{algo}/{heuristic}/'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    image_name = f"image_{num}.png"
    plt.savefig(directory_path + image_name)
    plt.close(fig)


if __name__ == '__main__':
    algorithms = {
        'maximal_rectangle': ['best_area'],
        # 'maximal_rectangle': ['best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside', 'bottom_left', 'contact_point'],
        # 'guillotine': ['best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside'],
        # 'skyline': ['bottom_left', 'best_fit']
    }

    for algo in algorithms:
        for heuristic in algorithms[algo]:
            M = g.BinManager(SLAB_LENGTH,SLAB_WIDTH, pack_algo=algo, heuristic=heuristic, rotation=True, sorting=True, wastemap=True)
            
            demoList = []    
            total_tiles = 0
            ROOT_DIR = Path(__file__).resolve().parent.parent
            filepath = f'{ROOT_DIR}/static/csv/tiles_data_4.csv'

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

            print(f"Algo: {algo}, Heuristic: {heuristic}, Total Tiles: {total_tiles}, Bins: {len(M.bins)}")

            plots = []
            total_bins_used = len(M.bins)
            slab_total_area = SLAB_LENGTH * SLAB_WIDTH
            global_total_area = SLAB_LENGTH * SLAB_WIDTH * total_bins_used
            for bin in M.bins:
                slab_details = {}
                plotList = []
                area_occupied = 0
                for rectangle in bin.items:
                    area_occupied += rectangle.area
                    plotList.append({"width": rectangle.width, "height": rectangle.height, "x": rectangle.x, "y": rectangle.y})

                percentage_occupied = round((area_occupied / slab_total_area) * 100, 3)
                slab_details['slab_percentage_occupied'] = percentage_occupied
                slab_details['slab_percentage_wasted'] = round(100 - percentage_occupied, 3)
                slab_details['rectangles'] = plotList
                plots.append(slab_details)

            count = 0
            for slab_data in plots:
                plot_graph(slab_data, count, algo, heuristic, total_bins_used)
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