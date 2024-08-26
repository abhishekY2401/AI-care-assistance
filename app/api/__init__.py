from .agent_resource import QueryAgentAPI, HealthAPI
from flask import Blueprint
agent_blueprint = Blueprint('agent_blueprint', __name__)


def add_resources(api):
    """ INIT API ROUTES """
    api.add_resource(QueryAgentAPI, '/query_llm')
    api.add_resource(HealthAPI, '/health_check')
