import json
import os
import shutil
import zipfile
from pathlib import Path
from django.core.files import File
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from bin_packing.models import Panel
from bin_packing.utils import custom_data_input, plot_graph


def index(request):
    if request.method == 'POST':
        context = {}
        inventory_input_type = request.POST.get('inventory_input_type')
        slab_length = request.POST.get('slab_length', None)
        slab_width = request.POST.get('slab_width', None)

        if slab_length and slab_width:
            result = None
            if inventory_input_type == 'manual':
                lengths = request.POST.getlist('length[]')
                widths = request.POST.getlist('width[]')
                quantities = request.POST.getlist('quantity[]')

                inventory_data = [{'length': float(length), 'width': float(width), 'quantity': int(quantity)}
                                  for length, width, quantity in zip(lengths, widths, quantities)]
                result = custom_data_input(inventory_data=inventory_data, upload_type='manual', algo='maximal_rectangle',
                                           heuristic='best_area', slab_l=float(slab_length), slab_w=float(slab_width))


            elif inventory_input_type == 'csv':
                csv_file = request.FILES.get('csv_file')
                result = custom_data_input(upload_type='csv', algo='maximal_rectangle', heuristic='best_area',
                                           filename=csv_file, slab_l=float(slab_length), slab_w=float(slab_width))

                panel_obj = Panel.objects.create(csv_file=csv_file, json_file=json.dumps(result))
                context['uploaded_csv_file_id'] = panel_obj.id

            global_total_area_percentage = result['global_total_area_used'] / (result['slab_total_area'] * result['total_bins_used']) * 100
            global_waste_area_percentage = 100 - global_total_area_percentage
            global_total_area_wasted = result['slab_total_area'] * result['total_bins_used'] - result['global_total_area_used']

            context['result'] = result
            context['global_area_percentage'] = round(global_total_area_percentage, 2)
            context['global_waste_area_percentage'] = round(global_waste_area_percentage, 2)
            context['global_total_area_wasted'] = round(global_total_area_wasted, 2)
            context['unique_layouts_count'] = len(result['plots'])
            context['slab_l'] = slab_length
            context['slab_w'] = slab_width
            context['show_statistics'] = True
            return render(request, 'index.html', context)

        return HttpResponse('Invalid Request, Provide Slab Length and Width', status=400)
    return render(request,'index.html')


def zip_file_handle(request):
    if request.method == 'POST':
        csv_file_id = request.POST.get('uploaded_csv_file_id')
        csv_file_obj = Panel.objects.filter(id=csv_file_id)
        if csv_file_obj.exists():
            csv_obj = csv_file_obj[0]
            data = json.loads(csv_obj.json_file)
            count = 0
            for slab_data in data['plots']:
                plot_graph(slab_data, count, data['total_bins_used'], csv_file_id)
                count += 1

            ROOT_DIR = Path(__file__).resolve().parent.parent
            zip_filename = f'{csv_file_id}.zip'
            folder_path = f'{ROOT_DIR}/media/{csv_file_id}'
            zip_file_path = f'{ROOT_DIR}/media/{csv_file_id}.zip'

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

