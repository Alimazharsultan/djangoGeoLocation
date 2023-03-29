from django.urls import path
from .views import calculate_distance_view, unitrack, speedTrack, topographic

app_name = 'measurements'

urlpatterns = [
    path('', unitrack, name='unitrack'),
    path('speed', speedTrack, name='unitrack'),
    path('topographic', topographic, name='topographic'),
    path('test', calculate_distance_view, name='calaculate-view'),
]