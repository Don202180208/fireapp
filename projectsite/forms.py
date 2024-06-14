from django import forms
from fire.models import Incident, FireStation, Locations, Firefighters, FireTruck, WeatherConditions

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['location', 'date_time', 'severity_level', 'description']

class FireStationForm(forms.ModelForm):
    class Meta:
        model = FireStation
        fields = '__all__'  # Or specify the fields you want in the form

class LocationsForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = ['name', 'latitude', 'longitude', 'address', 'city', 'country']

class FirefightersForm(forms.ModelForm):
    class Meta:
        model = Firefighters
        fields = ['name', 'rank', 'experience_level', 'station']

class FireTruckForm(forms.ModelForm):
    class Meta:
        model = FireTruck
        fields = ['truck_number', 'model', 'capacity', 'station']

class WeatherConditionsForm(forms.ModelForm):
    class Meta:
        model = WeatherConditions
        fields = ['incident', 'temperature', 'humidity', 'wind_speed', 'weather_description']