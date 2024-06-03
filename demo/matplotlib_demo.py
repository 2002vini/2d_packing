"""
Matplotlib binpack demo
"""
from typing import List
from random import randint
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Patch
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import greedypacker as g
import csv

from greedypacker.maximal_rectangles import MaximalRectangle



def get_vertices(i: g.Item, margin: int = 0.0) -> List[int]:
    print(type(i))
    print("print i.x",i.x)
    corners = [(i.x, i.y), 
            (i.x+i.width, i.y),
            (i.x+i.width, i.y+i.height),
            (i.x, i.y+i.height)]
    if margin:
        scalar = margin
        corners = [(i.x + scalar, i.y + scalar), 
                   (i.x + i.width - scalar, i.y + scalar),
                   (i.x + i.width - scalar, i.y + i.height - scalar),
                   (i.x + scalar, i.y + i.height - scalar)]
    return corners

def generate_path(i: g.Item, margin: float = 0.0) -> Path:
    vertices = []
    codes = []
    codes += [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
    vertices += get_vertices(i, margin) + [(0, 0)]

    vertices = np.array(vertices, float) 
    return Path(vertices, codes)

# def generate_path(items: List[g.Item], margin: bool = False) -> Path:
#    vertices = []
#    codes = []
#    for i in items:
#        codes += [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
#        vertices += get_vertices(i, margin) + [(0, 0)]

#    vertices = np.array(vertices, float) 
#    return Path(vertices, codes)

def draw_wastemap(binpack: g.BinManager) -> None:
    path = generate_path(binpack.bins[0].wastemap.freerects)            
    return PathPatch(path, lw=2.0, fc='white', edgecolor='orange', hatch='/',  label='wastemap')
    

def render_bin(binpack: g.BinManager, save: bool = False) -> None:
    fig, ax = plt.subplots()
    for Item in binpack.items:
        path = generate_path(Item)
        packed_item = PathPatch(path, facecolor='blue', edgecolor='green', label='packed items')
        ax.add_patch(packed_item)
    handles = [packed_item]
    
    if binpack.pack_algo == 'shelf':
        vertices = []
        codes = []
        for shelf in binpack.bins[0].shelves:
            codes += [Path.MOVETO] + [Path.LINETO] + [Path.CLOSEPOLY]
            vertices += [(0, shelf.vertical_offset), (shelf.x, shelf.vertical_offset), (0, 0)]
        vertices = np.array(vertices, int)
        path = Path(vertices, codes)
        shelf_border = PathPatch(path, lw=2.0, fc='red', edgecolor='red', label='shelf')
        handles.append(shelf_border)
        ax.add_patch(shelf_border)

    if binpack.pack_algo == 'skyline':
        vertices = []
        codes = []
        for seg in binpack.bins[0].skyline:
            codes += [Path.MOVETO] + [Path.LINETO] + [Path.CLOSEPOLY]
            vertices += [(seg.x, seg.y), (seg.x+seg.width, seg.y), (0, 0)]
        vertices = np.array(vertices, int)
        path = Path(vertices, codes)
        skyline = PathPatch(path, lw=2.0, fc='red', edgecolor='red', label='skyline')
        ax.add_patch(skyline)
        handles.append(skyline)

        wastemap = draw_wastemap(binpack)
        handles.append(wastemap)
        ax.add_patch(wastemap)
    
    if binpack.pack_algo == 'guillotine':
        path = generate_path(binpack.bins[0].freerects, True)
        freerects = PathPatch(path, fc='none', edgecolor='red', hatch='/', lw=1, label='freeRectangles')
        ax.add_patch(freerects)
        handles.append(freerects)
            
    if binpack.pack_algo == 'maximal_rectangle':
        margin = 0.04
        for rect in binpack.bins[0].freerects:
            path = generate_path(rect, margin=margin)
            freerects = PathPatch(path, fc='none', ec='red', lw=1, label='freeRectangles')
            ax.add_patch(freerects)
            margin += .02
        handles.append(freerects)
        
    ax.set_title('%s Algorithm - %r Heuristic' % (M.pack_algo, M.heuristic))
    ax.set_xlim(0, M.bin_width)
    ax.set_ylim(0, M.bin_height)
    
    plt.legend(handles=handles, bbox_to_anchor=(1.04,1), loc="upper left")


    if save:
        plt.savefig('%s Algorithm - %r Heuristic' % (M.pack_algo, M.heuristic), bbox_inches="tight", dpi=150)
    else:
        plt.show()
    return

def plotGraph(rectangles,num):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 2655)
    ax.set_ylim(0, 2100)
    ax.set_title('MaximalRectangle1 Placements')

    # Plot each rectangle
    for rect in rectangles:
        patch = patches.Rectangle((rect['x'], rect['y']), rect['width'], rect['height'], linewidth=1, edgecolor='b', facecolor='blue', alpha=0.5)
        ax.add_patch(patch)

    # Set aspect of the plot to be equal
    ax.set_aspect('equal', adjustable='box')

    # Save plot to a file instead of showing it
    image_name = f"image_{count}.png"
    plt.savefig('/Users/vinihundlani/Desktop/greedypacker/'+image_name)

if __name__ == '__main__':
    M = g.BinManager(2655,2100, pack_algo='maximal_rectangle', heuristic='best_area', rotation=True, sorting=True, wastemap=True)
    # M = g.BinManager(2655, 2100, pack_algo='guillotine', heuristic='best_shortside', rotation=False, sorting=False)
    # guillotine = [g.Item(2,3), g.Item(2,2), g.Item(2,1), g.Item(2,3), g.Item(2,2), g.Item(3,2)]
    # maximal = [g.Item(2,3), g.Item(3,3), g.Item(4,1), g.Item(2,3), g.Item(2,2), g.Item(1,2)]
    # shelf = [g.Item(2,3), g.Item(2,2), g.Item(2,1), g.Item(3,2), g.Item(1,1), g.Item(6,3), g.Item(3,2), g.Item(3,2), g.Item(4,2), g.Item(4,1)]
    # skyline = [g.Item(3,2), g.Item(2,1), g.Item(4,2), g.Item(1,3), g.Item(4,2), g.Item(2,3), g.Item(2, 2)]
    # demoList=[g.Item(900,320),g.Item(900,320),g.Item(900,320),g.Item(900,320),g.Item(900,320),g.Item(900,320),g.Item(900,320),g.Item(900,320),g.Item(900,320),g.Item(386,310),g.Item(386,310),g.Item(386,310),g.Item(386,310),g.Item(386,310),g.Item(860,320),g.Item(860,320),g.Item(564,310),g.Item(452,293),g.Item(720,530),g.Item(720,530),g.Item(696,530),g.Item(696,100)]
    # print(demoList)
    # render_bin(M, save=True)
    

    demoList = []    
    with open('../demo_data.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            height = float(row['height'])
            width = float(row['width'])
            quantity = row['quantity']
            
            for _ in range(int(quantity)):
                demoList.append(g.Item(height, width))
    
    M.add_items(*demoList)
    M.execute()

    print(len(M.bins))
    
    plots=[]
    for bin in M.bins:
        plotList = []
        for item in bin.items:
            plotList.append({"width": item.width, "height": item.height, "x": item.x, "y":item.y})
            # print(f"Height: {item.height}, Width: {item.width}, X: {item.x}, Y: {item.y}")
        plots.append(plotList)
    
    count=0
    for plot in plots:
        plotGraph(plot,count)
        count+=1


