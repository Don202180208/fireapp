from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation, WeatherConditions
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth, ExtractDay, ExtractHour, TruncMonth
from django.db.models import Count, F, Avg
from datetime import datetime, timedelta
from forms import IncidentForm
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
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')
    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
    fireStations_list = list(fireStations)

    context = {
        'fireStations': fireStations_list,
    }
    return render(request, 'map_station.html', context)

def map_incident(request):
    selected_city = request.GET.get('city')
    if selected_city:
        incidents = Incident.objects.filter(location__city=selected_city).values('id', 'description', 'severity_level', 'location__name', 'location__latitude', 'location__longitude')
    else:
        incidents = Incident.objects.values('id', 'description', 'severity_level', 'location__name', 'location__latitude', 'location__longitude')
    
    cities = Locations.objects.values_list('city', flat=True).distinct()
    context = {
        'incidents': list(incidents),
        'cities': cities,
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
