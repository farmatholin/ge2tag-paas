from flask import Flask

from gtbaas.gt_tool import GtTool
from gtbaas.server.daemon import Daemon

app = Flask(__name__)

tool = GtTool()


@app.route("/")
def hello():
    return 'Good morning sir'

def start():
    pass

def stop():
    pass

def create():
    pass



def run_server(port):
    app.run(port=port)


class MyDaemon(Daemon):
    def __init__(self, pidfile, port=5000):
        Daemon.__init__(self, pidfile)
        self.port = port

    def run(self):
        app.run(port=self.port)
