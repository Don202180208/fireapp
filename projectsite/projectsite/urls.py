from django.contrib import admin
from django.urls import path
from fire.views import (
    HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, 
    MultilineIncidentTop3Country, multipleBarbySeverity, map_station, 
    bar_chart_incidents_by_day, doughnut_chart_incidents_by_type, 
    heatmap_incidents_by_time_of_day, bubble_chart_incidents_by_location_severity, 
    line_chart_incident_trends
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name='home'),
    path('dashboard_chart/', ChartView.as_view(), name='dashboard-chart'),
    path('pie-severity/', PieCountbySeverity, name='pie-severity'),
    path('line-count-chart/', LineCountbyMonth, name='line-count-chart'),
    path('multiline-chart/', MultilineIncidentTop3Country, name='multiline-chart'),
    path('multiple-bar-severity/', multipleBarbySeverity, name='multiple-bar-severity'),
    path('map_station/', map_station, name='map-station'),
    path('bar-chart-incidents-by-day/', bar_chart_incidents_by_day, name='bar-chart-incidents-by-day'),
    path('doughnut-chart-incidents-by-type/', doughnut_chart_incidents_by_type, name='doughnut-chart-incidents-by-type'),
    path('heatmap-incidents-by-time-of-day/', heatmap_incidents_by_time_of_day, name='heatmap-incidents-by-time-of-day'),
    path('bubble-chart-incidents-by-location-severity/', bubble_chart_incidents_by_location_severity, name='bubble-chart-incidents-by-location-severity'),
    path('line-chart-incident-trends/', line_chart_incident_trends, name='line-chart-incident-trends'),
]
