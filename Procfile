web: gunicorn zuperscore.wsgi --workers 3 -k gevent --worker-connections 100 --config gunicorn_config.py
worker: celery -A zuperscore worker -l info
