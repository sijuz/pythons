# -*- coding: utf-8 -*-
from flask import Flask, make_response, jsonify
from configs.config import Config
from api.errors import ApiErrors
from flask_cors import CORS
import requests
import socket
import json
import traceback

exc = ApiErrors()
app = Flask(__name__)
app.config.from_object(Config)

if app.config['USE_CORS']:
    CORS(app, origins=app.config['CORS']['origins'],
         resources=app.config['CORS']['resources'],
         methods=app.config['CORS']['methods'])


@app.errorhandler(500)
def handler_500(error):
    requests.post(f'http://{app.config["ERROR_IP"]}/report', data=json.dumps({
        "key": app.config['ERROR_KEY'],
        "error": traceback.format_exc(),
        "host": str(socket.gethostbyname(socket.gethostname()))
    }))
    print(error)
    return exc.return_error(500), 500


@app.errorhandler(404)
def handler_404(error):
    return exc.return_error(404), 404


@app.errorhandler(405)
def handler_405(error):
    return exc.return_error(405), 405
