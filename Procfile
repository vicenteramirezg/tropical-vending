web: gunicorn vendingapp.wsgi --log-file - --timeout 1200 --workers 4 --threads 2
release: python manage.py migrate 