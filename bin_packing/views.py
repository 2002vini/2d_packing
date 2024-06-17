import csv
import json
import os
import shutil
import zipfile
from io import StringIO
from pathlib import Path
from django.core.files.base import ContentFile, File
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from bin_packing.models import Panel
from bin_packing.utils import plot_graph, create_pdf_file,custom_data_processing

def serialize_custom_item(item):
    if item is None:
        return None
    print("serializing custom data...")
    return {
        'width': item['width'],
        'height': item['height'],
        'x': item['x'],
        'y': item['y'],
        'code': item['code'],
        'polish_edge_l': item['polish_edge_l'],
        'polish_edge_w': item['polish_edge_w'],
        'thickness': item['thickness'],
        'child_items': serialize_custom_item(item['child_items'])  # Recursive call for linked items
    }
def serialize_plot_data(plot_data):
    for plot in plot_data['plots']:
        for idx, rect in enumerate(plot['rectangles']):
            # Serialize each CustomItem in the rectangles list
            for children in plot['rectangles'][idx]['child_items']:
                print(children)
                plot['rectangles'][idx]['child_items'][children] = serialize_custom_item(children)

def tuple_to_list(data):
    if isinstance(data, tuple):
        return [tuple_to_list(item) for item in data]
    elif isinstance(data, list):
        return [tuple_to_list(item) for item in data]
    elif isinstance(data, dict):
        return {key: tuple_to_list(value) for key, value in data.items()}
    else:
        return data

def create_csv_file(inventory_data):
    csv_file = StringIO()
    writer = csv.DictWriter(csv_file, fieldnames=['length', 'width', 'quantity'])
    writer.writeheader()
    for data in inventory_data:
        writer.writerow(data)
    csv_file.seek(0)                # Move cursor to beginning of StringIO object to read its content
    return csv_file

def create_dict(new_result):
    keys = ['width', 'height', 'x', 'y', 'code', 'thickness', 'polish_edge_l', 'polish_edge_w','child_items']
                
    for item in new_result['plots']:
        for rectangle in item['rectangles']:  
            dict_list=[]                      
            for rect in rectangle['child_items']:
                item_dict = dict(zip(keys, rect))
                dict_list.append(item_dict)
            rectangle['child_items']=dict_list
    return new_result

def index(request):
    if request.method == 'POST':
        context = {}
        inventory_input_type = request.POST.get('inventory_input_type')
        slab_length = request.POST.get('slab_length', None)
        slab_width = request.POST.get('slab_width', None)

        if slab_length and slab_width:
            result = None
            panel_obj = None
            if inventory_input_type == 'manual':
                lengths = request.POST.getlist('length[]')
                widths = request.POST.getlist('width[]')
                quantities = request.POST.getlist('quantity[]')

                inventory_data = [{'length': float(length), 'width': float(width), 'quantity': int(quantity)}
                                  for length, width, quantity in zip(lengths, widths, quantities)]

                # Create CSV file of inventory data
                csv_file = create_csv_file(inventory_data)

                # Save CSV file to Panel model
                panel_obj = Panel()
                panel_obj.csv_file.save('inventory_data.csv', ContentFile(csv_file.getvalue(), 'inventory_store_notebook'), save=True)
                csv_file.close()

                filename = panel_obj.csv_file.name.split('/')[-1]
                # result = custom_data_input(algo='maximal_rectangle', heuristic='best_area', filename=filename,
                #                            slab_l=float(slab_length), slab_w=float(slab_width))
                result=custom_data_processing(algo='maximal_rectangle', heuristic='best_area', filename=filename,
                                         slab_l=float(slab_length), slab_w=float(slab_width))
                
                panel_obj.json_file = json.dumps(result)
                panel_obj.save()

            elif inventory_input_type == 'csv':
                csv_file = request.FILES.get('csv_file')
                panel_obj = Panel.objects.create(csv_file=csv_file)
                result=custom_data_processing(algo='maximal_rectangle', heuristic='best_area', filename=csv_file,
                                         slab_l=float(slab_length), slab_w=float(slab_width))
                # result = custom_data_input(algo='maximal_rectangle', heuristic='best_area', filename=csv_file,
                #                            slab_l=float(slab_length), slab_w=float(slab_width))
                new_result=tuple_to_list(result)
                #converting child items to list of dictionary
                new_result=create_dict(new_result)
                result=create_dict(result)
                
                panel_obj.json_file = json.dumps(new_result)
                panel_obj.save()

            global_total_area_percentage = new_result['global_total_area_used'] / (new_result['slab_total_area'] * new_result['total_bins_used']) * 100
            global_waste_area_percentage = 100 - global_total_area_percentage
            global_total_area_wasted = new_result['slab_total_area'] * new_result['total_bins_used'] - new_result['global_total_area_used']

            context['result'] = result
            context['global_area_percentage'] = round(global_total_area_percentage, 2)
            context['global_waste_area_percentage'] = round(global_waste_area_percentage, 2)
            context['global_total_area_wasted'] = round(global_total_area_wasted, 2)
            context['unique_layouts_count'] = len(new_result['plots'])
            context['slab_l'] = slab_length
            context['slab_w'] = slab_width
            context['show_statistics'] = True
            context['panel_obj_id'] = panel_obj.id
            print("result passing in context is:",context['result'])
            create_pdf_file(context)

            return render(request, 'index.html', context)

        return HttpResponse('Invalid Request, Provide Slab Length and Width', status=400)
    return render(request, 'index.html')


def zip_file_handle(request):
    if request.method == 'POST':
        panel_id = request.POST.get('panel_obj_id')
        panel_obj = Panel.objects.filter(id=panel_id)
        if panel_obj.exists():
            csv_obj = panel_obj[0]
            data = json.loads(csv_obj.json_file)
            count = 0
            for slab_data in data['plots']:
                plot_graph(slab_data, count, data['total_bins_used'], panel_id)
                count += 1

            ROOT_DIR = Path(__file__).resolve().parent.parent
            zip_filename = f'{panel_id}.zip'
            folder_path = f'{ROOT_DIR}/media/{panel_id}'
            zip_file_path = f'{ROOT_DIR}/media/{panel_id}.zip'

            # Ensure the directory exists
            os.makedirs(folder_path, exist_ok=True)

            # Create zip_file of our folder
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))

            # Save zip_file in our database
            with open(zip_file_path, 'rb') as f:
                csv_obj.zip_file.save(zip_filename, File(f), save=True)

            # Remove the original folder
            shutil.rmtree(folder_path)
            os.remove(zip_file_path)    # remove temp zip file

            # messages.success(request, 'Download Successful')
            return JsonResponse({'url': csv_obj.zip_file.url}, status=200)
        return HttpResponse('Error: Requested csv file doesn\'t exists', status=400)

