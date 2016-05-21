import json
import logging

from flask import Flask, request, jsonify

from gtbaas.gt_tool import GtTool
from gtbaas.server.daemon import Daemon

app = Flask(__name__)

tool = GtTool()
log = logging.getLogger(__name__)


@app.route("/")
def hello():
    return jsonify({
        'code':200,
        "data":
            {
                'message': 'Good morning sir'
            }
    })


@app.route("/start", methods=['POST'])
def start():
    content = request.get_json(silent=True)
    if 'user' and 'container' in content.keys():
        tool.start(content['user'], content['container'])
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
        tool.stop(content['user'], content['container'])
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
        tool.create(content['user'], content['container'])
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
        tool.delete(content['user'], content['container'])
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
