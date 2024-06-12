import os
import django
import random
from faker import Faker
from django.utils import timezone

# Set up Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectsite.settings")
django.setup()

# Import your models
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions

# Create a Faker instance with Filipino locale
fake = Faker('fil_PH')

def generate_locations():
    for _ in range(10):
        Locations.objects.create(
            name=fake.street_name(),
            latitude=fake.latitude(),
            longitude=fake.longitude(),
            address=fake.address(),
            city=fake.city(),
            country='Philippines'
        )

def generate_incidents():
    locations = list(Locations.objects.all())
    SEVERITY_CHOICES = ['Minor Fire', 'Moderate Fire', 'Major Fire']
    for _ in range(30):
        Incident.objects.create(
            location=random.choice(locations),
            date_time=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc),
            severity_level=random.choice(SEVERITY_CHOICES),
            description=fake.text(max_nb_chars=250)
        )

def generate_firestations():
    for _ in range(10):
        FireStation.objects.create(
            name=fake.company(),
            latitude=fake.latitude(),
            longitude=fake.longitude(),
            address=fake.address(),
            city=fake.city(),
            country='Philippines'
        )

def generate_firefighters():
    XP_CHOICES = [
        'Probationary Firefighter', 'Firefighter I', 'Firefighter II', 
        'Firefighter III', 'Driver', 'Captain', 'Battalion Chief'
    ]
    for _ in range(20):
        Firefighters.objects.create(
            name=fake.name(),
            rank=random.choice(XP_CHOICES),
            experience_level=random.choice(XP_CHOICES)
        )

def generate_firetrucks():
    firestations = list(FireStation.objects.all())
    for _ in range(10):
        FireTruck.objects.create(
            truck_number=fake.bothify(text='Truck-###'),
            model=fake.word(),
            capacity=fake.random_int(min=1000, max=10000),
            station=random.choice(firestations)
        )

def generate_weatherconditions():
    incidents = list(Incident.objects.all())
    for _ in range(30):
        WeatherConditions.objects.create(
            incident=random.choice(incidents),
            temperature=fake.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=15, max_value=40),
            humidity=fake.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=20, max_value=100),
            wind_speed=fake.pydecimal(left_digits=2, right_digits=2, positive=False, min_value=0, max_value=20),
            weather_description=fake.sentence(nb_words=6)
        )

# Call the functions to generate fake data
generate_locations()
generate_incidents()
generate_firestations()
generate_firefighters()
generate_firetrucks()
generate_weatherconditions()

print("Fake data generation completed.")
