from django.http import HttpResponse
from django.shortcuts import render, redirect
from bin_packing.matplotlib_demo import custom_data_input


def index(request):
    return render(request,'index.html')


def receive_panels(request):
    if request.method == 'POST':
        lengths = request.POST.getlist('length[]')
        widths = request.POST.getlist('width[]')
        quantities = request.POST.getlist('quantity[]')
        
        inventory_data = [{'length': float(length), 'width': float(width), 'quantity': int(quantity)}
                  for length, width, quantity in zip(lengths, widths, quantities)]

        result = custom_data_input(inventory_data=inventory_data, upload_type='manual', algo='maximal_rectangle', heuristic='best_area')
        global_area_percentage = result['global_total_area'] / (result['slab_total_area'] * result['total_bins_used']) * 100
        global_waste_area_percentage = 100 - global_area_percentage

        context = {}
        context['result'] = result
        context['global_area_percentage'] = round(global_area_percentage, 2)
        context['global_waste_area_percentage'] = round(global_waste_area_percentage)
        return render(request, 'index.html', context)
    return HttpResponse('Invalid Request', status=400)
