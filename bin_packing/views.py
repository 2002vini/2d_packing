import json
from django.http import HttpResponse
from django.shortcuts import render, redirect


def index(request):
    return render(request,'index.html')


def receive_panels(request):
    if request.method == 'POST':
        lengths = request.POST.getlist('length[]')
        widths = request.POST.getlist('width[]')
        quantities = request.POST.getlist('quantity[]')
        
        panels = [{'length': float(length), 'width': float(width), 'quantity': int(quantity)}
                  for length, width, quantity in zip(lengths, widths, quantities)]

        print(json.dumps(panels, indent=4))

        return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))
    return HttpResponse('Invalid Request', status=400)
