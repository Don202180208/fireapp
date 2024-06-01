from django.contrib import admin
from django.urls import path
from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity, map_station

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name='home'),
    path('dashboard_chart/', ChartView.as_view(), name='dashboard-chart'),
    path('pie-severity/', PieCountbySeverity, name='pie-severity'),
    path('line-count-chart/', LineCountbyMonth, name='line-count-chart'),
    path('multiline-chart/', MultilineIncidentTop3Country, name='multiline-chart'),
    path('multiple-bar-severity/', multipleBarbySeverity, name='multiple-bar-severity'),
    path('map_station/', map_station, name='map-station'),
]
