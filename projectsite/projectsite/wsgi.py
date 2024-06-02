"""
WSGI config for projectsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Add the PythonAnywhere virtual environment path
venv_path = '/home/Fireapp2024/.virtualenvs/myenv/bin/activate_this.py'
exec(open(venv_path).read())

# Adjust the Python path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectsite.settings")
os.environ["PATH"] += os.pathsep + '/home/Fireapp2024/.local/bin'
os.environ["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

application = get_wsgi_application()

