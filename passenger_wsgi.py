import os
import sys

project_directory = '/home9/narenjis/narenji/narenji'
sys.path.insert(0, project_directory)

# اضافه کردن مسیر محیط مجازی
venv_site_packages = '/home9/narenjis/virtualenv/narenji/narenji/3.9/lib/python3.9/site-packages'
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

# تنظیمات Django - در config.settings است
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
