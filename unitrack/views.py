from turtle import color, speed
from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm, Locationfields
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium
import numpy as np
from folium import plugins
from folium.plugins import HeatMap
import csv
# Create your views here.
filename = '04-04-2022_coming_office.csv'
time_row = 1
date_row = 3
temp_row = 4
hum_row = 5
pres_row = 6
lat_row = 7
lon_row = 8
speed_row = 9
altitude_row= None

def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None
    
    
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')

    ip = '111.68.97.204'
    country, city, lat, lon = get_geo(ip)
    location = geolocator.geocode(city)

    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)
    # initial folium map
    m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon), zoom_start=8)
    # location marker
    folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
                    icon=folium.Icon(color='purple')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)
        # distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # folium map modification
        m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
        # location marker
        folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
                    icon=folium.Icon(color='purple')).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination,
                    icon=folium.Icon(color='red', icon='cloud')).add_to(m)


        # draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=5, color='blue')
        m.add_child(line)
        
        instance.location = location
        instance.distance = distance
        instance.save()
    
    m = m._repr_html_()

    context = {
        'distance' : distance,
        'destination': destination,
        'form': form,
        'map': m,
    }

    return render(request, 'measurements/main.html', context)


def unitrack(request):
    lon_points = []
    lat_points = []
    speed_points = []
    dateTimeIn = ''
    marked = False
    geolocator = Nominatim(user_agent='measurements')
    ip = '111.68.97.204'
    country, city, lat, lon = get_geo(ip)
    location = geolocator.geocode(city)

    # location coordinates
    l_lat = lat
    l_lon = lon

    form = Locationfields(request.POST or None)

    
    
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                lon_points.append(float(row[lon_row]))
                lat_points.append(float(row[lat_row]))
                speed_points.append(row[speed_row])
                # print(f'\t{row[1]} {row[3]} {row[5]} {row[6]} {row[7]} {row[8]} {row[9]}.')
                line_count += 1
        # print(f'Processed {line_count} lines.')
    pointA = (lat_points[0], lon_points[0])
    pointB = (lat_points[-1], lon_points[-1])
    
    if form.is_valid():
        dateTimeIn = form.cleaned_data.get('date_time_input')
        Date = str(dateTimeIn.day).zfill(2)+"-"+str(dateTimeIn.month).zfill(2)+"-"+str(dateTimeIn.year)
        Time = str(dateTimeIn.hour)+":"+str(dateTimeIn.minute).zfill(2)+":"+str(dateTimeIn.second).zfill(2)
        print(Date)
        print(Time)
        with open('04-04-2022_coming_office.csv') as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')
            
            for row in csv_reader:
                if Date==str(row[date_row]) and Time==str(row[time_row]):
                    print('same')
                    m = folium.Map(width=800, height=500, location=[float(row[7]), float(row[8])], zoom_start=12)
                    marked = True
                    # destination marker
                    folium.Marker([float(row[lat_row]), float(row[lon_row])], tooltip="Speed:"+row[9]+" Temperature: "+row[4], 
                                icon=folium.Icon(color='red', icon='cloud')).add_to(m)
    if not marked:
        distance = round(geodesic(pointA, pointB).km, 2)
        m = folium.Map(width=800, height=500, location=get_center_coordinates(lat_points[0], lon_points[0],lat_points[-1], lon_points[-1], ), zoom_start=get_zoom(distance))
        # location marker
    # folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
    #             icon=folium.Icon(color='purple')).add_to(m)
    
    listt=[]
    for i in range(0,len(lat_points), int(len(lat_points)/100)):
        listt.append(i)
    for i in (listt):
        # print(float(lon_points[i]), float(lat_points[i]))
        if i == 0:
            folium.Marker([lat_points[i], lon_points[i]],popup="Start",icon=folium.Icon(color="green", icon="play")).add_to(m)
        if i==listt[-1]:
            folium.Marker([lat_points[i], lon_points[i]],popup="Stop",icon=folium.Icon(color="red", icon="stop")).add_to(m)
        if (float(speed_points[i])>120):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='red', stroke=True, color='red').add_to(m)
        elif (float(speed_points[i])>100):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='orange', stroke=True, color='orange').add_to(m)
        elif (float(speed_points[i])>80):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='blue', stroke=True, color='blue').add_to(m)
        elif (float(speed_points[i])>40):            
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='green', stroke=True, color='green').add_to(m)
        elif (float(speed_points[i])>20):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='yellow', stroke=True, color='yellow').add_to(m)
        else:
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='white', stroke=True, color='white').add_to(m)
        

        # destination marker
    
    
    m = m._repr_html_()
    context = {
        'map': m,
        'form': form,
        'usman':'usmannnnnn'
    }

    return render(request, 'measurements/unitrack.html', context)

def speedTrack(request):
    lon_points = []
    lat_points = []
    speed_points = []
    dateTimeIn = ''
    marked = False
    geolocator = Nominatim(user_agent='measurements')
    ip = '111.68.97.204'
    country, city, lat, lon = get_geo(ip)
    location = geolocator.geocode(city)

    # location coordinates
    l_lat = lat
    l_lon = lon

    form = Locationfields(request.POST or None)
    
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                lon_points.append(float(row[8]))
                lat_points.append(float(row[7]))
                speed_points.append(float(row[9]))
                # print(f'\t{row[1]} {row[3]} {row[5]} {row[6]} {row[7]} {row[8]} {row[9]}.')
                line_count += 1
        # print(f'Processed {line_count} lines.')
    pointA = (lat_points[0], lon_points[0])
    pointB = (lat_points[-1], lon_points[-1])
    
    if form.is_valid():
        dateTimeIn = form.cleaned_data.get('date_time_input')
        Date = str(dateTimeIn.day).zfill(2)+"-"+str(dateTimeIn.month).zfill(2)+"-"+str(dateTimeIn.year)
        Time = str(dateTimeIn.hour).zfill(2)+":"+str(dateTimeIn.minute).zfill(2)+":"+str(dateTimeIn.second).zfill(2)
        with open('04-04-2022_coming_office') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            
            for row in csv_reader:
                if Date==row[3] and Time==row[1]:
                    m = folium.Map(width=800, height=500, location=[float(row[7]), float(row[8])], zoom_start=12)
                    marked = True
                    # destination marker
                    folium.Marker([float(row[7]), float(row[8])], tooltip="Speed:"+row[9]+" Temperature: "+row[4], 
                                icon=folium.Icon(color='red', icon='cloud')).add_to(m)
    if not marked:
        distance = round(geodesic(pointA, pointB).km, 2)
        m = folium.Map(width=800, height=500, location=get_center_coordinates(lat_points[0], lon_points[0],lat_points[-1], lon_points[-1], ), zoom_start=get_zoom(distance))
        # location marker
    # folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
    #             icon=folium.Icon(color='purple')).add_to(m)

    redpoints = []
    orangepoints = []
    bluepoints = []
    greenpoints = []
    yellowpoints = []
    whitepoints = []

    points = []
    current_state = 'w'
    listt=[]
    for idx, x in enumerate(speed_points):
        if x<1:
            folium.Marker([lat_points[idx], lon_points[idx]],tooltip='Speed: '+str(speed_points[idx]),popup="Sudden Stop",icon=folium.Icon(color="green", icon="stop")).add_to(m)

    for i in range(0,len(lat_points), int(len(lat_points)/100)):
        listt.append(i)

    for i in (listt):
        # print(float(lon_points[i]), float(lat_points[i]))
        
        if i == 0:
            folium.Marker([lat_points[i], lon_points[i]],popup="Start",icon=folium.Icon(color="green", icon="play")).add_to(m)
        if i==listt[-1]:
            folium.Marker([lat_points[i], lon_points[i]],popup="End",icon=folium.Icon(color="red", icon="stop")).add_to(m)
        if (float(speed_points[i])>120):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='red', stroke=True, color='red').add_to(m)
        elif (float(speed_points[i])>100):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='orange', stroke=True, color='orange').add_to(m)
        elif (float(speed_points[i])>80):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='blue', stroke=True, color='blue').add_to(m)
        elif (float(speed_points[i])>40):            
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='green', stroke=True, color='green').add_to(m)
        elif (float(speed_points[i])>20):
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='yellow', stroke=True, color='yellow').add_to(m)
        else:
            folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Speed: '+str(speed_points[i]),radius=5,weight=2,fill=True,fill_color='white', stroke=True, color='white').add_to(m)
        
    for i in range(0,len(lat_points)):
        # print(float(lon_points[i]), float(lat_points[i]))
        try:
            if current_state=='r':
                if (float(speed_points[i])>120):
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>100):
                    current_state='o'
                    folium.PolyLine(points, color="red", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>80):
                    current_state='b'
                    folium.PolyLine(points, color="red", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>40): 
                    current_state='g'
                    folium.PolyLine(points, color="red", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>20):
                    current_state='y'
                    folium.PolyLine(points, color="red", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                else:
                    current_state='w'
                    folium.PolyLine(points, color="red", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
            if current_state=='o':
                if (float(speed_points[i])>120):
                    current_state='r'
                    folium.PolyLine(points, color="orange", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>100):
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>80):
                    current_state='b'
                    folium.PolyLine(points, color="orange", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>40): 
                    current_state='g'
                    folium.PolyLine(points, color="orange", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>20):
                    current_state='y'
                    folium.PolyLine(points, color="orange", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                else:
                    current_state='w'
                    folium.PolyLine(points, color="orange", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
            if current_state=='b':
                if (float(speed_points[i])>120):
                    current_state='r'
                    folium.PolyLine(points, color="blue", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>100):
                    current_state='o'
                    folium.PolyLine(points, color="blue", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>80):
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>40): 
                    current_state='g'
                    folium.PolyLine(points, color="blue", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>20):
                    current_state='y'
                    folium.PolyLine(points, color="blue", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                else:
                    current_state='w'
                    folium.PolyLine(points, color="blue", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
            if current_state=='g':
                if (float(speed_points[i])>120):
                    current_state='r'
                    folium.PolyLine(points, color="green", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>100):
                    current_state='o'
                    folium.PolyLine(points, color="green", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>80):
                    current_state='b'
                    folium.PolyLine(points, color="green", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>40):            
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>20):
                    current_state='y'
                    folium.PolyLine(points, color="green", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                else:
                    current_state='w'
                    folium.PolyLine(points, color="green", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
            if current_state=='y':
                if (float(speed_points[i])>120):
                    current_state='r'
                    folium.PolyLine(points, color="yellow", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>100):
                    current_state='o'
                    folium.PolyLine(points, color="yellow", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>80):
                    current_state='b'
                    folium.PolyLine(points, color="yellow", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>40):            
                    current_state='g'
                    folium.PolyLine(points, color="yellow", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>20):
                    points.append(tuple([lat_points[i], lon_points[i]]))
                else:
                    current_state='w'
                    folium.PolyLine(points, color="yellow", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
            if current_state=='w':
                if (float(speed_points[i])>120):
                    current_state='r'
                    folium.PolyLine(points, color="white", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>100):
                    current_state='o'
                    folium.PolyLine(points, color="white", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>80):
                    current_state='b'
                    folium.PolyLine(points, color="white", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>40):            
                    current_state='g'
                    folium.PolyLine(points, color="white", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                elif (float(speed_points[i])>20):
                    current_state='y'
                    folium.PolyLine(points, color="white", weight=5, opacity=1).add_to(m)
                    points = []
                    points.append(tuple([lat_points[i], lon_points[i]]))
                else:
                    points.append(tuple([lat_points[i], lon_points[i]]))
        except:
            pass
        


        

                

        # destination marker
    # print(redpoints)
    # folium.PolyLine(redpoints, color="red", weight=5, opacity=1).add_to(m)
    # folium.PolyLine(orangepoints, color="orange", weight=5, opacity=1).add_to(m)
    # folium.PolyLine(bluepoints, color="blue", weight=5, opacity=1).add_to(m)
    # folium.PolyLine(greenpoints, color="green", weight=5, opacity=1).add_to(m)
    # folium.PolyLine(yellowpoints, color="yellow", weight=5, opacity=1).add_to(m)
    # folium.PolyLine(whitepoints, color="white", weight=5, opacity=1).add_to(m)


    
    m = m._repr_html_()
    context = {
        'map': m,
        'form': form,
    }

    return render(request, 'measurements/speed.html', context)

def topographic(request):
    # lon_points = []
    # lat_points = []
    # speed_points = []
    # dateTimeIn = ''
    # marked = False
    # geolocator = Nominatim(user_agent='measurements')
    # ip = '111.68.97.204'
    # country, city, lat, lon = get_geo(ip)
    # location = geolocator.geocode(city)

    # # location coordinates
    # l_lat = lat
    # l_lon = lon

    form = Locationfields(request.POST or None)
    # elevation_points = []
    # with open(filename) as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     line_count = 0
        
    #     for row in csv_reader:
    #         if line_count == 0:
    #             # print(f'Column names are {", ".join(row)}')
    #             line_count += 1
    #         else:
    #             lon_points.append(float(row[6]))
    #             lat_points.append(float(row[5]))
    #             speed_points.append(row[7])
    #             elevation_points.append(row[8])
    #             # print(f'\t{row[1]} {row[3]} {row[5]} {row[6]} {row[7]} {row[8]} {row[9]}.')
    #             line_count += 1
    #     # print(f'Processed {line_count} lines.')
    # pointA = (lat_points[0], lon_points[0])
    # pointB = (lat_points[-1], lon_points[-1])
    
    # if form.is_valid():
    #     dateTimeIn = form.cleaned_data.get('date_time_input')
    #     Date = str(dateTimeIn.day).zfill(2)+"-"+str(dateTimeIn.month).zfill(2)+"-"+str(dateTimeIn.year)
    #     Time = str(dateTimeIn.hour).zfill(2)+":"+str(dateTimeIn.minute).zfill(2)+":"+str(dateTimeIn.second).zfill(2)
    #     with open('19-03-2022.csv') as csv_file:
    #         csv_reader = csv.reader(csv_file, delimiter=',')
            
    #         for row in csv_reader:
    #             if Date==row[3] and Time==row[1]:
    #                 m = folium.Map(width=800, height=500, location=[float(row[6]), float(row[8])], zoom_start=12)
    #                 marked = True
    #                 # destination marker
    #                 folium.Marker([float(row[7]), float(row[8])], tooltip="Elevation:"+row[8]+" Temperature: "+row[4], 
    #                             icon=folium.Icon(color='red', icon='cloud')).add_to(m)
    # if not marked:
    #     distance = round(geodesic(pointA, pointB).km, 2)
    #     m = folium.Map(width=1000, height=600, location=get_center_coordinates(lat_points[0], lon_points[0],lat_points[-1], lon_points[-1], ), zoom_start=get_zoom(distance))
    #     # location marker
    # # folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
    # #             icon=folium.Icon(color='purple')).add_to(m)

    # for i in range(0,len(elevation_points)):
    #     # print(float(lon_points[i]), float(lat_points[i]))
    #     if (float(elevation_points[i])>550):
    #         folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Elevation Point: '+elevation_points[i],radius=5,weight=2,fill=True,fill_color='red', stroke=True, color='red').add_to(m)
    #     elif (float(elevation_points[i])>545):
    #         folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Elevation Point: '+elevation_points[i],radius=5,weight=2,fill=True,fill_color='orange', stroke=True, color='orange').add_to(m)
    #     elif (float(elevation_points[i])>540):
    #         folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Elevation Point: '+elevation_points[i],radius=5,weight=2,fill=True,fill_color='blue', stroke=True, color='blue').add_to(m)
    #     elif (float(elevation_points[i])>530):            
    #         folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Elevation Point: '+elevation_points[i],radius=5,weight=2,fill=True,fill_color='green', stroke=True, color='green').add_to(m)
    #     elif (float(elevation_points[i])>520):
    #         folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Elevation Point: '+elevation_points[i],radius=5,weight=2,fill=True,fill_color='yellow', stroke=True, color='yellow').add_to(m)
    #     else:
    #         folium.CircleMarker([lat_points[i], lon_points[i]],tooltip='Elevation Point: '+elevation_points[i],radius=5,weight=2,fill=True,fill_color='white', stroke=True, color='white').add_to(m)      
    lon, lat = -86.276, 30.935 
    zoom_start = 5
    data = (
        np.random.normal(size=(100, 3)) *
        np.array([[1, 1, 1]]) +
        np.array([[48, 5, 1]])
    ).tolist()
    m = folium.Map([48, 5], tiles='stamentoner', zoom_start=6)

    # HeatMap(data).add_to(folium.FeatureGroup(name='Heat Map').add_to(m))
    folium.LayerControl().add_to(m)
    
    m = m._repr_html_()
    context = {
        'map': m,
        'form': form,
    }

    return render(request, 'measurements/topographic.html', context)