import os
import sys

# Add the project root to Python's path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Tell Django which settings to use
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopease.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()