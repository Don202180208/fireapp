from django.contrib import admin
from django.urls import path
from fire.views import (
    HomePageView, ChartView, pie_chart_incidents_by_severity, line_chart_incidents_over_time, 
    MultilineIncidentTop3City, multipleBarbySeverity, map_station, map_incident, create_incident, update_incident, delete_incident,
    bar_chart_incidents_by_day, doughnut_chart_incidents_by_type, 
    heatmap_incidents_by_time_of_day, bubble_chart_weather_conditions, 
    line_chart_incident_trends, radar_chart_weather_conditions
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name='home'),
    path('dashboard_chart/', ChartView.as_view(), name='dashboard-chart'),
    path('pie-severity/', pie_chart_incidents_by_severity, name='pie-severity'),
    path('line_chart_incidents_over_time/', line_chart_incidents_over_time, name='line_chart_incidents_over_time'),
    path('multiline-chart/', MultilineIncidentTop3City, name='multiline-chart'),
    path('multiple-bar-severity/', multipleBarbySeverity, name='multiple-bar-severity'),
    path('map_station/', map_station, name='map-station'),
    path('map_incident/', map_incident, name='map-incident'),
    path('create_incident/', create_incident, name='create-incident'),
    path('update_incident/<int:id>/', update_incident, name='update-incident'),
    path('delete_incident/<int:id>/', delete_incident, name='delete-incident'),
    path('bar-chart-incidents-by-day/', bar_chart_incidents_by_day, name='bar-chart-incidents-by-day'),
    path('doughnut-chart-incidents-by-type/', doughnut_chart_incidents_by_type, name='doughnut-chart-incidents-by-type'),
    path('radar_chart_data/', radar_chart_weather_conditions, name='radar_chart_data'),
    path('heatmap-incidents-by-time-of-day/', heatmap_incidents_by_time_of_day, name='heatmap-incidents-by-time-of-day'),
    path('bubble_chart_weather_conditions/', bubble_chart_weather_conditions, name='bubble_chart_weather_conditions'),
    path('line-chart-incident-trends/', line_chart_incident_trends, name='line-chart-incident-trends'),
]
