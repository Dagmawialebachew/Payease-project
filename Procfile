web: gunicorn laborers.wsgi --log-file -

web: python manage.py migrate && gunicorn laborers.wsgi