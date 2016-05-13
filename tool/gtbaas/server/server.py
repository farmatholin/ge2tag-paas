from flask import Flask

from gtbaas.gt_tool import GtTool

app = Flask(__name__)

tool = GtTool()


@app.route("/")
def hello():
    return "Hello World!"


def run_server(port, daemon):
    app.run(port=port)
