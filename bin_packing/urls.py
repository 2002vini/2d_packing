from django.urls import path
from .views import index, receive_panels


app_name = 'bin_packing'


urlpatterns = [
    path('', index, name='index'),
    path('receive_panels/', receive_panels, name='receive_panels'),
]
