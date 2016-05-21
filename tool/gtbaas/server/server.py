import json
import logging
import random

from flask import Flask, request, jsonify
from celery import Celery

from gtbaas.gt_tool import GtTool
from gtbaas.server.daemon import Daemon

app = Flask(__name__)

tool = GtTool()
log = logging.getLogger(__name__)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@app.route("/")
def hello():
    return jsonify({
        'code': 200,
        "data":
            {
                'message': 'Good morning sir',
                'rand': random.random(),
            }
    })


@celery.task()
def start_container(content):
    return tool.start(content['user'], content['container'])


@celery.task()
def stop_container(content):
    return tool.stop(content['user'], content['container'])


@celery.task()
def create_container(content):
    return tool.create(content['user'], content['container'])


@celery.task()
def remove_container(content):
    return tool.delete(content['user'], content['container'])


@app.route("/start", methods=['POST'])
def start():
    content = request.get_json(silent=True)
    if 'user' and 'container' in content.keys():
        res = start_container.delay(content)
        #res.wait()
        return jsonify({
            "code": 200,
            "data":
                {
                    "message": "Container start",
                    "host": "{}-{}.{}".format(
                        content['container'],
                        content['user'],
                        tool.config.site
                    )
                }
        })
    log.info(json.dumps(content))
    return jsonify({
        "code": 400,
        "data":
            {
                "message": "Required data 'user' and 'container'",
            }
    })


@app.route("/stop", methods=['POST'])
def stop():
    content = request.get_json(silent=True)
    if 'user' and 'container' in content.keys():
        res = stop_container.delay(content)
        #res.wait()
        return jsonify({
            "code": 200,
            "data":
                {
                    "message": "Container stopped",
                }
        })
    log.info(json.dumps(content))
    return jsonify({
        "code": 400,
        "data":
            {
                "message": "Required data 'user' and 'container'",
            }
    })


@app.route("/create", methods=['POST'])
def create():
    content = request.get_json(silent=True)
    if 'user' and 'container' in content.keys():
        res = create_container.delay(content)
        #res.wait()
        return jsonify({
            "code": 200,
            "data":
                {

                    "message": "Container Created",
                    "host": "{}-{}.{}".format(
                        content['container'],
                        content['user'],
                        tool.config.site
                    )
                }
        })
    log.info(json.dumps(content))
    return jsonify({
        "code": 400,
        "data":
            {
                "message": "Required data 'user' and 'container'",
            }
    })


@app.route("/remove", methods=['POST'])
def remove():
    content = request.get_json(silent=True)
    if 'user' and 'container' in content.keys():
        res = remove_container.delay(content)
       # res.wait()
        return jsonify({
            "code": 200,
            "data":
                {
                    "message": "Container removed",
                }
        })
    log.info(json.dumps(content))
    return jsonify({
        "code": 400,
        "data":
            {
                "message": "Required data 'user' and 'container'",
            }
    })


def run_server(port):
    app.run(host='0.0.0.0', port=port)


class MyDaemon(Daemon):
    def __init__(self, pidfile, port=8000):
        Daemon.__init__(self, pidfile)
        self.port = port

    def run(self):
        app.run(host='0.0.0.0', port=self.port)

    # if __name__ == "__main__":
    #  app.run(host='0.0.0.0', port=8000)
