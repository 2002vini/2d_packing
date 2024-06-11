import matplotlib.pyplot as plt
import matplotlib.patches as patches
import greedypacker as g
import csv
import os
import uuid
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

SLAB_LENGTH = 138
SLAB_WIDTH = 78

def draw_nested_shapes(x, y, width, height, shapes, filename='plot.png'):
    """
    Draw a rectangle and nest various shapes inside it, saving the plot to a file.

    Parameters:
    x, y: Coordinates of the bottom-left corner of the rectangle.
    width, height: Dimensions of the rectangle.
    shapes: A list of tuples describing the shapes to be drawn inside the rectangle.
    filename: Name of the file to save the plot.
    """
    fig, ax = plt.subplots()
    # Draw the outer rectangle
    outer_rect = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor='g', facecolor='none')
    ax.add_patch(outer_rect)

    # Process each shape in the list
    for shape in shapes:
        type_shape = shape[0]
        x_offset, y_offset = shape[1], shape[2]
        params = shape[3:]

        if type_shape == 'rectangle':
            # Expecting parameters: height, width
            height, width = params
            rect = patches.Rectangle((x + x_offset, y + y_offset), width, height, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        elif type_shape == 'L-shape':
            # Expecting parameters: width, length, thickness
            width, length, thickness = params
            vertical = patches.Rectangle((x + x_offset, y + y_offset), thickness, length, linewidth=1, edgecolor='b', facecolor='none')
            horizontal = patches.Rectangle((x + x_offset, y + y_offset), width, thickness, linewidth=1, edgecolor='b', facecolor='none')
            ax.add_patch(vertical)
            ax.add_patch(horizontal)

        elif type_shape == 'complex-partition':
            # Expecting parameters: total_width, total_height, inner_width, inner_height, thickness
            total_width, total_height, inner_width, inner_height, thickness = params
            outer = patches.Rectangle((x + x_offset, y + y_offset), total_width, total_height, linewidth=1, edgecolor='purple', facecolor='none')
            ax.add_patch(outer)
            vertical = patches.Rectangle((x + x=>x_offset, y + y_offset), thickness, inner_height, linewidth=1, edgecolor='b', facecolor='none')
            horizontal = patches.Rectangle((x + x_offset, y + y_offset), inner_width, thickness, linewidth=1, edgecolor='b', facecolor='none')
            ax.add_patch(vertical)
            ax.add_patch(horizontal)
            square = patches.Rectangle((x + x_offset + thickness, y + y_offset + thickness), inner_width - thickness, inner_height - thickness, linewidth=1, edgecolor='blue', facecolor='none')
            ax.add_patch(square)

    plt.axis('scaled')
    plt.savefig(filename)
    plt.close()


def plot_graph(slab_data, num, algo, heuristic, total_bins_used, csv_file_id, csv_file_path):
    print("plotting graph...")
    print(slab_data)
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
        print(f"id is {rect['id']}")
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
    directory_path = f'{ROOT_DIR}/media/zip_file/{csv_file_id}/'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    image_name = f"image_{num+1}.png"
    plt.savefig(directory_path + image_name)
    plt.close(fig)

def sortListRectangles(list):
    sorted_items = sorted(list, key=lambda item: item.width * item.height, reverse=True)
    return sorted_items
def custom_data_input(upload_type, algo, heuristic, inventory_data=None, filename=None, slab_l=138, slab_w=78):
    SLAB_LENGTH = slab_l
    SLAB_WIDTH = slab_w
    M = g.BinManager(SLAB_LENGTH, SLAB_WIDTH, pack_algo=algo, heuristic=heuristic, rotation=True, sorting=True, wastemap=True)
    demoList = []
    LShape_present=False
    LShape_List=[]

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
                    unique_id = str(item['code'])
                    height = float(item['length'])
                    width = float(item['width'])
                    quantity = int(item['quantity'])
                    thickness=float(item['thickness'])
                    if thickness > 0:
                        LShape_present=True
                        for _ in range(int(quantity)):
                            LShape_List.append(g.Item(width, height,unique_id,thickness))
                    else:
                        for _ in range(int(quantity)):
                            demoList.append(g.Item(width, height,id))
                if LShape_present:
                    sortedList=sortListRectangles(demoList)
                    LShape_List=sortListRectangles(LShape_List)
                    print(len(LShape_List))
                    #find largest rectanglw which can fit inside it
                    #dimensions can be:
                    for tile in LShape_List:
                        print(tile)
                        sortedList.sort(key=lambda item: item.width * item.height, reverse=True)
                        max_length=tile.height-tile.thickness
                        max_width=tile.width-tile.thickness
                        print(f"max length that can be accomodated is {max_length}x{max_width}")
                        mappedList={}
                        included=False
                        for item in sortedList:
                            if min(item.height,item.width)<=min(max_length,max_width) and max(item.height,item.width)<=max(max_length,max_width):
                                #we can use that rectangle 
                                #create a new id
                                #insert that in sorted list
                                #sort that list again and map it to the new id which is generated
                                print(f"we can fit {item} int the remaining area")
                                if tile.height>=tile.width and item.height>=item.width:
                                    inner_height=item.height
                                    inner_width=item.width
                                elif tile.height>=tile.width and item.width>=item.height:
                                    inner_height=item.width
                                    inner_width=item.height
                                elif tile.width>=tile.height and item.width>=item.height:
                                    inner_width=item.width
                                    inner_height=item.height
                                else:
                                    inner_width=item.height
                                    inner_height=item.width
                                included=True
                                unique_id = str(uuid.uuid4())
                                mappedList[unique_id]=[item.id,tile.id]
                                sortedList.remove(item)
                                sortedList.append(g.Item(tile.width,tile.height,unique_id,tile.thickness,inner_width,inner_height))
                                break
                            else:
                                #we can't use that rectangle
                                pass
                        if not included:
                            #iska matlab l shape ke andar koi inscribe nahi ho sakta hai
                            sortedList.append(g.Item(tile.width,tile.height,tile.id,thickness))


        else:
            raise ValueError("Please provide a valid filename for CSV data.")

    M.add_items(*sortedList)
    M.execute()

    slab_configurations = {}
    print("printing slab configurations...")
    #agar innerLength,innerHeight=0 and thickness!=0--->l print karwana hai
    #agar innerLength,innerHeight!=0 l ke andar square print karana hai
    #agar width,innerHeight,innerlength=0 matlab normal rectangle
    shapes=[]
    for bin in M.bins:
        rectangles = [(rectangle.width, rectangle.height, rectangle.x, rectangle.y,rectangle.id,rectangle.thickness,rectangle.innerWidth,rectangle.innerHeight) for rectangle in bin.items]
        # Sort rectangles by position and size for consistent comparison
        rectangles.sort()
        for rect in rectangles:
            print(rect)
            if rect[5]<=0:
                shapes.append(['rectangle',rect[2],rect[3],rect[0],rect[1]])
            elif rect[5]>0 and rect[6]<=0:
                shapes.append(['LShape',rect[2],rect[3],rect[1],rect[0],rect[5]])
            else:
                shapes.append(['complex-partition',rect[2],rect[3],rect[0],rect[1],rect[6],rect[7],rect[5]])
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
    
    draw_nested_shapes(0, 0, slab_w, slab_l, shapes)

    return {
        "plots": plots,
        "total_bins_used": len(M.bins),
        "slab_total_area": slab_total_area,
        "global_total_area_used": global_total_area_used,
        "slab_length": slab_l,
        "slab_width": slab_w
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

