import json
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request,'index.html')


def receive_panels(request):
    if request.method == 'POST':
        lengths = request.POST.getlist('length[]')
        widths = request.POST.getlist('width[]')
        quantities = request.POST.getlist('quantity[]')
        
        panels = [{'length': float(length), 'width': float(width), 'quantity': int(quantity)}
                  for length, width, quantity in zip(lengths, widths, quantities)]
        
        # Do something with the panels data
        # For demonstration, convert it to JSON and print it
        print(json.dumps(panels, indent=4))
        
        return HttpResponse('Data Received', content_type="text/plain")

    return HttpResponse('Invalid Request', status=400)