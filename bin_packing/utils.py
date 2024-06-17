import matplotlib.pyplot as plt
import matplotlib.patches as patches
import greedypacker as g
import csv
import os
from pathlib import Path
from greedypacker.item import CustomItem
from bin_packing.plot_pdf import draw_heading_container, draw_stats_container, draw_main_container
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from django.conf import settings
import uuid

SLAB_LENGTH = 138
SLAB_WIDTH = 78
cutting_blade_margin_5mm = 0.2    # considering 1 point == 1 inch

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
            vertical = patches.Rectangle((x + x_offset, y + y_offset), thickness, inner_height, linewidth=1, edgecolor='b', facecolor='none')
            horizontal = patches.Rectangle((x + x_offset, y + y_offset), inner_width, thickness, linewidth=1, edgecolor='b', facecolor='none')
            ax.add_patch(vertical)
            ax.add_patch(horizontal)
            square = patches.Rectangle((x + x_offset + thickness, y + y_offset + thickness), inner_width - thickness, inner_height - thickness, linewidth=1, edgecolor='blue', facecolor='none')
            ax.add_patch(square)

    plt.axis('scaled')
    plt.savefig(filename)
    plt.close()

def sortListRectangles(list):
    sorted_items = sorted(list, key=lambda item: item.width * item.height, reverse=True)
    return sorted_items

def plot_graph(slab_data, num, total_bins_used, csv_file_id):
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


def create_pdf_file(context):
    c = canvas.Canvas(f"/Users/vinihundlani/Desktop/greedypacker/static/img/test.pdf", pagesize=A4, bottomup=0)
    # c = canvas.Canvas(f"{settings.BASE_DIR}/media/pdf/test.pdf", pagesize=A4, bottomup=0)
    result = context['result']
    margin = 1 * cm  # Set a margin for aesthetics
    current_y = margin  # Start from the bottom of the page plus a margin
    plots_per_page = 0

    heading_data = {
        'total_area_used': round(result['global_total_area_used'] / 144, 2),      # divide by 144 to get area in sq. ft.
        'total_area_wasted': round(context['global_total_area_wasted'] / 144, 2), # divide by 144 to get area in sq. ft.
        'total_area_used_percent': context['global_area_percentage'],
        'total_area_wasted_percent': context['global_waste_area_percentage'],
        'total_no_of_slabs_used': result['total_bins_used'],
        'total_area_of_single_slab': round(result['slab_total_area'] / 144, 2),   # divide by 144 to get area in sq. ft.
        'slab_width': context['slab_l'],
        'slab_height': context['slab_w']
    }

    for idx, plot in enumerate(result['plots']):
        rectangles = plot['rectangles']

        total_rft = 0.0
        for rect in rectangles:
            rect_actual_width = rect['width'] - cutting_blade_margin_5mm
            rect_actual_height = rect['height'] - cutting_blade_margin_5mm
            total_rft += (rect['polish_edge_l'] * rect_actual_height) + (rect['polish_edge_w'] * rect_actual_width)
        stats_data = {
            'layout_number': idx + 1,
            'unique_layouts_count': context['unique_layouts_count'],
            'area_occupied': round(plot['slab_used_area'] / 144, 2),      # divide by 144 to get area in sq. ft.
            'area_wasted': round(plot['slab_wasted_area'] / 144, 2),      # divide by 144 to get area in sq. ft.
            'layout_count': plot['layout_count'],
            'area_occupied_percent': plot['slab_percentage_occupied'],
            'area_wasted_percent': plot['slab_percentage_wasted'],
            'total_rft': round(total_rft, 2),
        }
        page_width, page_height = A4
        needed_height = 0.3 * page_height + 0.115 * page_height  # main + stats containers height
        if current_y + needed_height > page_height - margin or plots_per_page == 2:
            c.showPage()
            current_y = margin
            plots_per_page = 0

        if idx == 0:
            heading_h, heading_y = draw_heading_container(c, heading_data)
            current_y += heading_h  # Adjust current_y to account for the height of the heading

        container_y, container_h = draw_main_container(c, current_y, 0, rectangles)  # heading_h is 0 for subsequent pages
        draw_stats_container(c, container_y, container_h, stats_data)

        # Update the current_y position and plots count
        current_y += container_h + 0.115 * page_height + margin
        plots_per_page += 1

    c.save()
def process_children(children):
    result = []
    for child in children:
        child_tuple = (
            child.width,
            child.height,
            child.x,
            child.y,
            child.code,
            child.thickness,
            child.polish_edge_l,
            child.polish_edge_w,
            process_children(child.child_items) if child.child_items else ()
        )
        result.append(child_tuple)
    return tuple(result)
def convert_to_tuples(rectangles):
    # Convert the main list and all child lists to tuples
    converted = []
    for rect in rectangles:
        # Convert each rectangle's children list to a tuple of tuples
        children = tuple(tuple(child) for child in rect[8])
        # Convert the entire rectangle to a tuple, replacing the children list with a tuple
        converted.append(rect[:8] + (children,))
    return converted
def custom_data_processing(algo,heuristic,filename=None,slab_l=138,slab_w=78):
    SLAB_LENGTH = slab_l
    SLAB_WIDTH = slab_w
    LShape_present=False
    LShape_List=[]
    sortedList=[]
    if filename:
        ROOT_DIR = Path(__file__).resolve().parent.parent
        file_path = f'{ROOT_DIR}/media/csv/{filename}'
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for item in csv_reader:
                height = float(item['length']) + cutting_blade_margin_5mm
                width = float(item['width']) + cutting_blade_margin_5mm
                quantity = int(item['quantity'])
                thickness=float(item['thickness'])
                code = item['code']
                polish_edge_l = int(item['polish_edge_l'])
                polish_edge_w = int(item['polish_edge_w'])

                for _ in range(int(quantity)):
                    if thickness>0:
                        LShape_present=True
                        LShape_List.append(CustomItem(height,width,code,polish_edge_l,polish_edge_w,thickness))
                    else:
                        sortedList.append(CustomItem(height, width,code, polish_edge_l, polish_edge_w))
            if LShape_present==True:
                LShape_List=sortListRectangles(LShape_List)
                for shape in LShape_List:
                    new_slab_length=shape.width-shape.thickness
                    new_slab_width=shape.height-shape.thickness
                    sortedList=sortListRectangles(sortedList)
                    newList=[]
                    for item in sortedList:
                        if min(item.width,item.height)<=min(new_slab_width,new_slab_length) and max(item.width,item.height)<=max(new_slab_length,new_slab_width):
                            newList.append(item)
                            # sortedList.remove(item)
                    M=g.BinManager(new_slab_length,new_slab_width,pack_algo=algo,heuristic=heuristic,rotation=True,sorting=True,wastemap=True)
                    M.add_items(*newList)
                    M.execute()
                    max_area=0.0
                    max_bin=None
                    max_bin_list=None
                    for bin in M.bins:
                        print("new item position inside l shape will be")
                        print(bin.items)
                        rectangles = [CustomItem(rectangle.width, rectangle.height,rectangle.code,rectangle.polish_edge_l,rectangle.polish_edge_w,rectangle.thickness,rectangle.child_items,(rectangle.x,rectangle.y)) for rectangle in bin.items]
                        area_occupied = sum(rect.width * rect.height for rect in rectangles)
                        if area_occupied>max_area:
                            max_area=area_occupied
                            max_bin_list=rectangles
                    #after we find the bin which occupies most area we have to modify the sorted list
                    #pehle toh we have to append the L shape and inside the L shape customitem we need to nest the 
                    #rectangles
                    shape.child_items=max_bin_list
                    sortedList.append(shape)
                    max_bin_codes = {item.code for item in max_bin_list}
                    #in the sorted list we need to ensure we remove items which are present in child_tems
                    sortedList = [item for item in sortedList if item.code not in max_bin_codes]
                
                #now after processing L shape we call the bin function again to process on all the rectangles
            M = g.BinManager(SLAB_LENGTH, SLAB_WIDTH, pack_algo=algo, heuristic=heuristic, rotation=True, sorting=True, wastemap=True)
            M.add_items(*sortedList)
            M.execute()
    else:
        raise ValueError("Please provide a valid filename.")
   
    slab_configurations = {}
    for bin in M.bins:

        rectangles = [
        (
            rectangle.width,
            rectangle.height,
            rectangle.x,
            rectangle.y,
            rectangle.code,
            rectangle.thickness,
            rectangle.polish_edge_l,
            rectangle.polish_edge_w,
            process_children(rectangle.child_items)
        ) 
        for rectangle in bin.items
        ]
        rectangles.sort(key=lambda r: (r[2], r[3], r[0]*r[1]))  # Sort by x, y, and area
        key = tuple(rectangles)
        print(type(key))
        if key in slab_configurations:
            slab_configurations[key] += 1
        else:
            slab_configurations[key] = 1
        # draw_nested_shapes(0,0,slab_l,slab_w,shapes)

    # Prepare data to return, incorporating counts of each unique slab configuration
    plots = []
    global_total_area_used = 0
    slab_total_area = SLAB_LENGTH * SLAB_WIDTH

    for config, count in slab_configurations.items():
        slab_details = {}
        plotList = [{"width": rect[0], "height": rect[1], "x": rect[2], "y": rect[3], "code": rect[4], "polish_edge_l": rect[6], "polish_edge_w": rect[7],"thickness":rect[5],"child_items":rect[8]} for rect in config]
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



    
# def custom_data_input(algo, heuristic, filename=None, slab_l=138, slab_w=78):
#     SLAB_LENGTH = slab_l
#     SLAB_WIDTH = slab_w
#     M = g.BinManager(SLAB_LENGTH, SLAB_WIDTH, pack_algo=algo, heuristic=heuristic, rotation=True, sorting=True, wastemap=True)
#     demoList = []
#     LShape_present=False
#     LShape_List=[]
#     if filename:
#         ROOT_DIR = Path(__file__).resolve().parent.parent
#         file_path = f'{ROOT_DIR}/media/csv/{filename}'
#         with open(file_path, mode='r') as file:
#             csv_reader = csv.DictReader(file)
#             for item in csv_reader:
#                 height = float(item['length']) + cutting_blade_margin_5mm
#                 width = float(item['width']) + cutting_blade_margin_5mm
#                 quantity = int(item['quantity'])
#                 thickness=float(item['thickness'])
#                 code = item['code']
#                 polish_edge_l = int(item['polish_edge_l'])
#                 polish_edge_w = int(item['polish_edge_w'])

#                 for _ in range(int(quantity)):
#                     if thickness>0:
#                         LShape_present=True
#                         LShape_List.append(CustomItem(height,width,code,polish_edge_l,polish_edge_w,thickness))
#                     else:
#                         demoList.append(CustomItem(height, width,code, polish_edge_l, polish_edge_w))
                
#                 #agar l shape present hoga
#                 #toh slab size remaining size ke equal kar do and uspe algo lagao
#                 #then nest the CustomItem result into it 
#                 if LShape_present:
#                     sortedList=sortListRectangles(demoList)
#                     LShape_List=sortListRectangles(LShape_List)
#                     print(len(LShape_List))
#                     #find largest rectanglw which can fit inside it
#                     #dimensions can be:
#                     for tile in LShape_List:
#                         print(tile)
#                         sortedList.sort(key=lambda item: item.width * item.height, reverse=True)
#                         max_length=tile.height-tile.thickness
#                         max_width=tile.width-tile.thickness
#                         print(f"max length that can be accomodated is {max_length}x{max_width}")
#                         mappedList={}
#                         included=False
#                         for item in sortedList:
#                             if min(item.height,item.width)<=min(max_length,max_width) and max(item.height,item.width)<=max(max_length,max_width):
#                                 #we can use that rectangle 
#                                 #create a new id
#                                 #insert that in sorted list
#                                 #sort that list again and map it to the new id which is generated
#                                 print(f"we can fit {item} int the remaining area")
#                                 if tile.height>=tile.width and item.height>=item.width:
#                                     inner_height=item.height
#                                     inner_width=item.width
#                                 elif tile.height>=tile.width and item.width>=item.height:
#                                     inner_height=item.width
#                                     inner_width=item.height
#                                 elif tile.width>=tile.height and item.width>=item.height:
#                                     inner_width=item.width
#                                     inner_height=item.height
#                                 else:
#                                     inner_width=item.height
#                                     inner_height=item.width
#                                 included=True
#                                 sortedList.remove(item)
#                                 print("l shape item is:",tile)
#                                 print("item we are adding is:",item)
#                                 sortedList.append(CustomItem(tile.width,tile.height,tile.code,polish_edge_l,polish_edge_w,tile.thickness,CustomItem(inner_width,inner_height,item.code,polish_edge_l,polish_edge_w,item.thickness)))
#                                 break
#                             else:
#                                 #we can't use that rectangle
#                                 pass
#                         if not included:
#                             #iska matlab l shape ke andar koi inscribe nahi ho sakta hai
#                             sortedList.append(CustomItem(tile.width,tile.height,tile.id,polish_edge_l,polish_edge_w,tile.thickness))
#                     print("list after processing is:",sortedList)

  

#     else:
#         raise ValueError("Please provide a valid filename.")

#     M.add_items(*sortedList)
#     M.execute()

#     slab_configurations = {}
#     for bin in M.bins:

#         rectangles = [(rectangle.width, rectangle.height, rectangle.x, rectangle.y, rectangle.code,rectangle.thickness,
#                        rectangle.polish_edge_l, rectangle.polish_edge_w,rectangle.next_item) for rectangle in bin.items]
#         # Sort rectangles by position and size for consistent comparison
#         rectangles.sort()
        
#         # Convert to a tuple for immutability and use as a dictionary key
#         key = tuple(rectangles)
#         if key in slab_configurations:
#             slab_configurations[key] += 1
#         else:
#             slab_configurations[key] = 1
#         # draw_nested_shapes(0,0,slab_l,slab_w,shapes)

#     # Prepare data to return, incorporating counts of each unique slab configuration
#     plots = []
#     global_total_area_used = 0
#     slab_total_area = SLAB_LENGTH * SLAB_WIDTH

#     for config, count in slab_configurations.items():
#         slab_details = {}
#         plotList = [{"width": rect[0], "height": rect[1], "x": rect[2], "y": rect[3], "code": rect[4], "polish_edge_l": rect[6], "polish_edge_w": rect[7],"thickness":rect[5],"next_item":rect[8]} for rect in config]
#         for rect in config:
#         # Unpack rectangle details
#             width, height, x, y, code, thickness, polish_edge_l, polish_edge_w, child_items = rect

#         # Calculate area based on the presence of thickness
#             if thickness > 0:
#                 area = (width * thickness) + (height * thickness)
#             else:
#                 area = width * height

#         # Include child items in the area calculation if they exist
#         for child in rect['child_items']:
#             child_width, child_height = child['width'], child['height']
#             child_thickness = child['thickness']
#             if child_thickness > 0:
#                 child_area = (child_width * child_thickness) + (child_height * child_thickness)
#             else:
#                 child_area = child_width * child_height
#             area += child_area

#         # Add the calculated area to the total area occupied by the slab
#         area_occupied += area
#         percentage_occupied = round((area_occupied / slab_total_area) * 100, 3)
#         global_total_area_used += area_occupied * count

#         slab_details["slab_percentage_occupied"] = percentage_occupied
#         slab_details["slab_percentage_wasted"] = round(100 - percentage_occupied, 3)
#         slab_details["rectangles"] = plotList
#         slab_details["layout_count"] = count
#         slab_details["slab_used_area"] = round(area_occupied, 2)
#         slab_details["slab_wasted_area"] = round(slab_total_area - area_occupied, 2)
#         plots.append(slab_details)
    
#     return {
#         "plots": plots,
#         "total_bins_used": len(M.bins),
#         "slab_total_area": slab_total_area,
#         "global_total_area_used": global_total_area_used
#     }

