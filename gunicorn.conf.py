# GUNICORN_CMD_ARGS="--bind=0.0.0.0 --workers=4 --reload=True --timeout=120 --worker-class gevent" gunicorn wsgi:app


bind = "0.0.0.0"
backlog = 64
worker_class = "gevent"
workers = 4
timeout = 120
worker_connections = 1000
keep_alive = 2
reload = "True"