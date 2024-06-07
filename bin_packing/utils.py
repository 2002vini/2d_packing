import matplotlib.pyplot as plt
import matplotlib.patches as patches
import greedypacker as g
import csv
import os
from pathlib import Path

SLAB_LENGTH = 138
SLAB_WIDTH = 78


def plot_graph(slab_data, num, algo, heuristic, total_bins_used, csv_file_id, csv_file_path):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, SLAB_LENGTH)
    ax.set_ylim(0, SLAB_WIDTH)
    ax.set_title(f'Layout: {num+1}/{total_bins_used}')
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
    stats_text = f"Total bins used: {total_bins_used}\nArea occupied: {slab_data['slab_percentage_occupied']}%\nArea wasted: {slab_data['slab_percentage_wasted']}%\nLayout Count: {slab_data['layout_count']}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    fig.text(0.5, 0.07, stats_text, ha='center', va='bottom', fontsize=10, bbox=props)
    fig.subplots_adjust(bottom=0.2)  # Increase the bottom margin

    # Check if the directory exists, create if not and save the image
    ROOT_DIR = Path(__file__).resolve().parent.parent
    directory_path = f'{ROOT_DIR}/media/{csv_file_id}/'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    image_name = f"image_{num+1}.png"
    plt.savefig(directory_path + image_name)
    plt.close(fig)


def custom_data_input(upload_type, algo, heuristic, inventory_data=None, filename=None, slab_l=138, slab_w=78):
    SLAB_LENGTH = slab_l
    SLAB_WIDTH = slab_w
    M = g.BinManager(SLAB_LENGTH, SLAB_WIDTH, pack_algo=algo, heuristic=heuristic, rotation=True, sorting=True, wastemap=True)
    demoList = []

    # Load data from manual input or CSV file
    if upload_type == 'manual':
        if inventory_data:
            for data in inventory_data:
                quantity = data['quantity']
                length = data['length']
                width = data['width']
                for _ in range(int(quantity)):
                    demoList.append(g.Item(length, width))
        else:
            raise ValueError("Please provide Inventory Data.")
    elif upload_type == 'csv':
        if filename:
            ROOT_DIR = Path(__file__).resolve().parent.parent
            file_path = f'{ROOT_DIR}/static/csv/{filename}'
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for item in csv_reader:
                    height = float(item['length'])
                    width = float(item['width'])
                    quantity = int(item['quantity'])
                    for _ in range(int(quantity)):
                        demoList.append(g.Item(height, width))
        else:
            raise ValueError("Please provide a valid filename for CSV data.")

    M.add_items(*demoList)
    M.execute()

    slab_configurations = {}
    for bin in M.bins:
        rectangles = [(rectangle.width, rectangle.height, rectangle.x, rectangle.y) for rectangle in bin.items]
        # Sort rectangles by position and size for consistent comparison
        rectangles.sort()
        # Convert to a tuple for immutability and use as a dictionary key
        key = tuple(rectangles)
        if key in slab_configurations:
            slab_configurations[key] += 1
        else:
            slab_configurations[key] = 1

    # Prepare data to return, incorporating counts of each unique slab configuration
    plots = []
    global_total_area_used = 0
    slab_total_area = SLAB_LENGTH * SLAB_WIDTH

    for config, count in slab_configurations.items():
        slab_details = {}
        plotList = [{"width": rect[0], "height": rect[1], "x": rect[2], "y": rect[3]} for rect in config]
        area_occupied = sum(rect[0] * rect[1] for rect in config)
        global_total_area_used += area_occupied * count
        percentage_occupied = round((area_occupied / slab_total_area) * 100, 3)

        slab_details["slab_percentage_occupied"] = percentage_occupied
        slab_details["slab_percentage_wasted"] = round(100 - percentage_occupied, 3)
        slab_details["rectangles"] = plotList
        slab_details["layout_count"] = count
        slab_details["slab_used_area"] = round(area_occupied, 2)
        slab_details["slab_wasted_area"] = round(slab_total_area - area_occupied, 2)
        plots.append(slab_details)

    return {
        "plots": plots,
        "total_bins_used": len(M.bins),
        "slab_total_area": slab_total_area,
        "global_total_area_used": global_total_area_used
    }


# if __name__ == '__main__':
#     algorithms = {
#         'maximal_rectangle': ['best_area'],
#         # 'maximal_rectangle': ['best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside', 'bottom_left', 'contact_point'],
#         # 'guillotine': ['best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside'],
#         # 'skyline': ['bottom_left', 'best_fit']
#     }
#
#     for algo in algorithms:
#         for heuristic in algorithms[algo]:
#             result = custom_data_input('csv', algo, heuristic, [], 'tiles_data_4.csv')
#
#             count = 0
#             for slab_data in result['plots']:
#                 plot_graph(slab_data, count, algo, heuristic, result['total_bins_used'])
#                 count += 1


# *** ACTUAL ANSWERS ***
# Tile Data 1: 131
# Tile Data 2: 63
# Tile Data 3: 42
# Tile Data 4: 10
# Tile Data 5: 54
# Tile Data 6: 72
# Tile Data 7: 14
# Tile Data 8: 98