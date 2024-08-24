from flask_restful import Resource, reqparse
from flask import jsonify

_query_parser = reqparse.RequestParser()


class QueryAgentAPI(Resource):

    def post(self):

        data = _query_parser.parse_args()

        # initialize imp parameters

        self.ticket_id = data['chat_context']['ticket_id']
        self.latest_query = data['latest_query']
        self.ideal_response = data['ideal_response']
        # self.generated_response = None


class HealthAPI(Resource):

    def get(self):
        return "Flask App Started!"
