from gtbaas.server.server import app, make_celery
celery = make_celery(app)
