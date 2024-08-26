from flask_restful import Resource, reqparse
from flask import jsonify, request
import os
from ..search import search_diet_plan
from ..utils import generate_response
from ..response_templates.response import sample_output
import json

# _query_parser = reqparse.RequestParser()

# _query_parser.add_argument('ticket_id', type=str,
#                            required=True, help='Ticket ID is required')
# _query_parser.add_argument('latest_query', type=list(dict),
#                            required=True, help='Latest query is required')
# _query_parser.add_argument('ideal_response', type=str,
#                            required=True, help='Ideal response is required')
# _query_parser.add_argument('chat_history', type=list(dict),
#                            required=True, help='Chat context is required')


class QueryAgentAPI(Resource):

    def post(self):

        data = request.get_json()
        print(data)

        # initialize imp parameters
        patient_url = os.environ['PATIENT_URL']
        print(patient_url)
        ticket_id = data['ticket_id']
        latest_query = data['latest_query']
        ideal_response = data['ideal_response']
        chat_history = data['chat_history']

        # self.generated_response = None

        # search patient's diet plan
        patient_diet_info = search_diet_plan(
            patient_url,
            ticket_id,
            latest_query,
            chat_history
        )

        # initialize prompt message

        prompt = f'''You are a doctor providing dietary advice based on a patient's diet chart and profile. A patient who has been checked by a doctor through Curelink has posted a query about their diet.

        Your task is to give actionable advice based on:
        1. The patient's chat history
        2. Their diet information
        3. Their overall profile

        Compare the patient's current diet to the recommended diet and provide advice on how to align the patient's eating habits with the prescribed diet. Include potential disadvantages of deviating from the diet plan.

        Here's the ideal response example: {ideal_response}

        Here are the patient's details in JSON format:
        {json.dumps(patient_diet_info)}

        Generate a response and an ideal response in the following JSON format:
        {{
            "generated_response": "<your generated response here>",
            "ideal_response": "<your ideal response here>"
        }}

        Ensure the response is concise, actionable, and adheres to the format provided.
        '''

        user_response = generate_response('command-r', prompt)

        try:
            user_response = user_response.strip()
            user_response = user_response.replace("\n", "")

            # Attempt to parse the LLM response as JSON
            response_json = json.loads(user_response)
            return jsonify(response_json)  # Return the response as JSON

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({"error": "Failed to parse LLM response as JSON"}), 500

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500


class HealthAPI(Resource):

    def get(self):
        return "Flask App Started!"
