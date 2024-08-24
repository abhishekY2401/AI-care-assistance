import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api


### FACTORY APP ###


def create_app():
    # Application Factory: Assembles and returns the copy of the app

    # init flask app
    app = Flask(__name__)
    app.config.from_object('settings')

    # add blueprints to flask app
    from .api import agent_blueprint, add_resources

    restful = Api(agent_blueprint, prefix="/api/v1")
    add_resources(restful)
    app.register_blueprint(agent_blueprint)

    return app
