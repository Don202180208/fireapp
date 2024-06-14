from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation, WeatherConditions, Firefighters, FireTruck
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth, ExtractDay, ExtractHour, TruncMonth
from django.db.models import Count, F, Avg
from datetime import datetime, timedelta
from forms import IncidentForm, FireStationForm,LocationsForm, FirefightersForm, FireTruckForm, WeatherConditionsForm
import json


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "chart.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

def pie_chart_incidents_by_severity(request):
    data = Incident.objects.values('severity_level').annotate(count=Count('id'))
    
    pie_chart_data = {
        'labels': [entry['severity_level'] for entry in data],
        'datasets': [{
            'data': [entry['count'] for entry in data],
            'backgroundColor': [
                '#f3545d',  # Color for severity level 1
                '#fdaf4b',  # Color for severity level 2
                '#1d7af3',  # Color for severity level 3
                '#1f9d55',  # Color for severity level 4
                '#a55eea'   # Color for severity level 5
            ]
        }]
    }
    
    return JsonResponse(pie_chart_data)

def line_chart_incidents_over_time(request):
    data = (Incident.objects
            .annotate(month=TruncMonth('date_time'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month'))
    
    # Prepare the data for the chart
    labels = [entry['month'].strftime('%Y-%m') for entry in data]
    datasets = [{
        'label': 'Number of Incidents',
        'data': [entry['count'] for entry in data],
        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
        'borderColor': 'rgba(75, 192, 192, 1)',
        'fill': False,
    }]

    line_chart_data = {
        'labels': labels,
        'datasets': datasets
    }

    return JsonResponse(line_chart_data)

def MultilineIncidentTop3City(request):
    query = '''
    SELECT
        fl.city,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM
        fire_incident fi
    JOIN
        fire_locations fl ON fi.location_id = fl.id
    WHERE
        fl.country = 'Philippines'  -- Assuming all locations are in the Philippines
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY
        fl.city, month
    ORDER BY
        fl.city, month;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    
    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    
    for row in rows:
        city = row[0]
        month = row[1]
        total_incidents = row[2]
        if city not in result:
            result[city] = {month: 0 for month in months}
        result[city][month] = total_incidents
    
    while len(result) < 3:
        missing_city = f"City {len(result) + 1}"
        result[missing_city] = {month: 0 for month in months}
    for city in result:
        result[city] = dict(sorted(result[city].items()))
    return JsonResponse(result)
    
def multipleBarbySeverity(request):
    query = '''
    SELECT
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM
        fire_incident fi
    GROUP BY
        fi.severity_level, month
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    
    for row in rows:
        severity_level = str(row[0])
        month = row[1]
        total_incidents = row[2]
        if severity_level not in result:
            result[severity_level] = {month: 0 for month in months}
        result[severity_level][month] = total_incidents
    
    for severity_level in result:
        result[severity_level] = dict(sorted(result[severity_level].items()))

    return JsonResponse(result)

def map_station(request):
    fireStations = FireStation.objects.all().values('id', 'name', 'latitude', 'longitude', 'address', 'city', 'country')
    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
    fireStations_list = list(fireStations)

    context = {
        'fireStations': fireStations_list,
    }
    return render(request, 'map_station.html', context)

def create_station(request):
    if request.method == 'POST':
        form = FireStationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('map_station')
    else:
        form = FireStationForm()

    context = {
        'form': form,
    }
    return render(request, 'create_station.html', context)

def update_station(request, station_id):
    station = get_object_or_404(FireStation, pk=station_id)
    if request.method == 'POST':
        form = FireStationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect('map_station')
    else:
        form = FireStationForm(instance=station)

    context = {
        'form': form,
        'station': station,
    }
    return render(request, 'update_station.html', context)

def delete_station(request, station_id):
    station = get_object_or_404(FireStation, id=station_id)
    if request.method == 'POST':
        station.delete()
        return redirect('map_station')

    context = {
        'station': station,
    }
    return render(request, 'delete_station.html', context)

# views.py
def map_incident(request):
    selected_city = request.GET.get('city')
    if selected_city:
        incidents = Incident.objects.filter(location__country='Philippines', location__city=selected_city).values(
            'id', 'description', 'severity_level', 'location__name', 'location__latitude', 'location__longitude'
        )
    else:
        incidents = Incident.objects.filter(location__country='Philippines').values(
            'id', 'description', 'severity_level', 'location__name', 'location__latitude', 'location__longitude'
        )

    # Convert Decimal values to floats
    incidents = [
        {
            **incident,
            'location__latitude': float(incident['location__latitude']),
            'location__longitude': float(incident['location__longitude'])
        }
        for incident in incidents
    ]

    # Debugging: Print incidents to the console
    for incident in incidents:
        print(f"Incident: {incident}")

    cities = Locations.objects.filter(country='Philippines').values_list('city', flat=True).distinct()
    context = {
        'incidents': incidents,
        'cities': list(cities),
        'selected_city': selected_city,
    }
    return render(request, 'map_incident.html', context)

def create_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('map-incident')
    else:
        form = IncidentForm()
    return render(request, 'incident_form.html', {'form': form})

def update_incident(request, id):
    incident = get_object_or_404(Incident, id=id)
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect('map-incident')
    else:
        form = IncidentForm(instance=incident)
    return render(request, 'incident_form.html', {'form': form})

def delete_incident(request, id):
    incident = get_object_or_404(Incident, id=id)
    if request.method == 'POST':
        incident.delete()
        return redirect('map-incident')
    return render(request, 'confirm_delete.html', {'incident': incident})
    
def bar_chart_incidents_by_day(request):
    data = Incident.objects.annotate(day_of_week=ExtractDay('date_time')).values('day_of_week').annotate(count=Count('id')).order_by('day_of_week')
    return JsonResponse(list(data), safe=False)

def doughnut_chart_incidents_by_type(request):
    # Group incidents by severity_level and count them
    data = Incident.objects.values('severity_level').annotate(count=Count('id'))
    
    chart_data = {
        "labels": [entry['severity_level'] for entry in data],
        "data": [entry['count'] for entry in data]
    }
    
    return JsonResponse(chart_data)

def radar_chart_weather_conditions(request):
    weather_conditions = WeatherConditions.objects.all()
    labels = [str(condition.incident.date_time) for condition in weather_conditions]
    temperatures = [float(condition.temperature) for condition in weather_conditions]
    humidities = [float(condition.humidity) for condition in weather_conditions]
    wind_speeds = [float(condition.wind_speed) for condition in weather_conditions]

    radar_data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Temperature',
                'data': temperatures,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'pointBackgroundColor': 'rgba(255, 99, 132, 1)',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': 'rgba(255, 99, 132, 1)',
            },
            {
                'label': 'Humidity',
                'data': humidities,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'pointBackgroundColor': 'rgba(54, 162, 235, 1)',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': 'rgba(54, 162, 235, 1)',
            },
            {
                'label': 'Wind Speed',
                'data': wind_speeds,
                'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                'borderColor': 'rgba(255, 206, 86, 1)',
                'pointBackgroundColor': 'rgba(255, 206, 86, 1)',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': 'rgba(255, 206, 86, 1)',
            },
        ]
    }

    return JsonResponse(radar_data)

def heatmap_incidents_by_time_of_day(request):
    data = Incident.objects.annotate(hour_of_day=ExtractHour('date_time')).values('hour_of_day').annotate(count=Count('id')).order_by('hour_of_day')
    return JsonResponse(list(data), safe=False)

def bubble_chart_weather_conditions(request):
    data = Incident.objects.values('severity_level').annotate(
        avg_temperature=Avg('weatherconditions__temperature'),
        avg_humidity=Avg('weatherconditions__humidity'),
        avg_wind_speed=Avg('weatherconditions__wind_speed')
    )

    bubble_chart_data = []
    severity_colors = {
        'Low': 'rgba(54, 162, 235, 0.6)',
        'Moderate': 'rgba(255, 206, 86, 0.6)',
        'High': 'rgba(255, 99, 132, 0.6)'
    }

    for entry in data:
        severity = entry['severity_level']
        bubble_chart_data.append({
            'label': severity,
            'temperature': entry['avg_temperature'],
            'humidity': entry['avg_humidity'],
            'wind_speed': entry['avg_wind_speed'],
            'backgroundColor': severity_colors.get(severity, 'rgba(75, 192, 192, 0.6)')
        })

    return JsonResponse(bubble_chart_data, safe=False)

def line_chart_incident_trends(request):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    data = Incident.objects.filter(date_time__range=(start_date, end_date)).annotate(month=ExtractMonth('date_time')).values('month').annotate(count=Count('id')).order_by('month')
    return JsonResponse(list(data), safe=False)

def dashboard(request):
    # Retrieve data for the new charts
    # Example: Retrieve fire incidents and severity levels
    fire_incidents = Incident.objects.all()
    # Pass data to the template
    context = {
        'fire_incidents': fire_incidents,
    }
    return render(request, 'chart.html', context)

def list_locations(request):
    locations = Locations.objects.all()
    return render(request, 'list_locations.html', {'locations': locations})

def create_location(request):
    if request.method == 'POST':
        form = LocationsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_locations')
    else:
        form = LocationsForm()
    return render(request, 'create_location.html', {'form': form})

def update_location(request, location_id):
    location = get_object_or_404(Locations, id=location_id)
    if request.method == 'POST':
        form = LocationsForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('list_locations')
    else:
        form = LocationsForm(instance=location)
    return render(request, 'update_location.html', {'form': form, 'location': location})

def delete_location(request, location_id):
    location = get_object_or_404(Locations, id=location_id)
    if request.method == 'POST':
        location.delete()
        return redirect('list_locations')
    return render(request, 'delete_location.html', {'location': location})

def list_firefighters(request):
    firefighters = Firefighters.objects.all()
    return render(request, 'list_firefighters.html', {'firefighters': firefighters})

def create_firefighter(request):
    if request.method == 'POST':
        form = FirefightersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_firefighters')
    else:
        form = FirefightersForm()
    return render(request, 'create_firefighter.html', {'form': form})

def update_firefighter(request, firefighter_id):
    firefighter = get_object_or_404(Firefighters, id=firefighter_id)
    if request.method == 'POST':
        form = FirefightersForm(request.POST, instance=firefighter)
        if form.is_valid():
            form.save()
            return redirect('list_firefighters')
    else:
        form = FirefightersForm(instance=firefighter)
    return render(request, 'update_firefighter.html', {'form': form, 'firefighter': firefighter})

def delete_firefighter(request, firefighter_id):
    firefighter = get_object_or_404(Firefighters, id=firefighter_id)
    if request.method == 'POST':
        firefighter.delete()
        return redirect('list_firefighters')
    return render(request, 'delete_firefighter.html', {'firefighter': firefighter})

def list_firetrucks(request):
    firetrucks = FireTruck.objects.all()
    return render(request, 'list_firetrucks.html', {'firetrucks': firetrucks})

def create_firetruck(request):
    if request.method == 'POST':
        form = FireTruckForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_firetrucks')
    else:
        form = FireTruckForm()
    return render(request, 'create_firetruck.html', {'form': form})

def update_firetruck(request, firetruck_id):
    firetruck = get_object_or_404(FireTruck, id=firetruck_id)
    if request.method == 'POST':
        form = FireTruckForm(request.POST, instance=firetruck)
        if form.is_valid():
            form.save()
            return redirect('list_firetrucks')
    else:
        form = FireTruckForm(instance=firetruck)
    return render(request, 'update_firetruck.html', {'form': form, 'firetruck': firetruck})

def delete_firetruck(request, firetruck_id):
    firetruck = get_object_or_404(FireTruck, id=firetruck_id)
    if request.method == 'POST':
        firetruck.delete()
        return redirect('list_firetrucks')
    return render(request, 'delete_firetruck.html', {'firetruck': firetruck})

def list_weather_conditions(request):
    weather_conditions = WeatherConditions.objects.all()
    return render(request, 'list_weather_conditions.html', {'weather_conditions': weather_conditions})

def create_weather_condition(request):
    if request.method == 'POST':
        form = WeatherConditionsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_weather_conditions')
    else:
        form = WeatherConditionsForm()
    return render(request, 'create_weather_condition.html', {'form': form})

def update_weather_condition(request, weather_condition_id):
    weather_condition = get_object_or_404(WeatherConditions, id=weather_condition_id)
    if request.method == 'POST':
        form = WeatherConditionsForm(request.POST, instance=weather_condition)
        if form.is_valid():
            form.save()
            return redirect('list_weather_conditions')
    else:
        form = WeatherConditionsForm(instance=weather_condition)
    return render(request, 'update_weather_condition.html', {'form': form, 'weather_condition': weather_condition})

def delete_weather_condition(request, weather_condition_id):
    weather_condition = get_object_or_404(WeatherConditions, id=weather_condition_id)
    if request.method == 'POST':
        weather_condition.delete()
        return redirect('list_weather_conditions')
    return render(request, 'delete_weather_condition.html', {'weather_condition': weather_condition})