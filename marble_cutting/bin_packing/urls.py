from django.urls import path, include
from .views import index


app_name = 'bin_packing'


urlpatterns = [
    path('', index, name='index'),
]
