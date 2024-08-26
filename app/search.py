import requests
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

meal_times = {
    "early morning": "6:30",
    "breakfast": "8:30",
    "mid meal": "11:00",
    "lunch": "13:30",
    "dinner": "20:00",
    "post dinner": "21:30"
}

meal_times_objects = {meal: datetime.strptime(
    t, "%H:%M").time() for meal, t in meal_times.items()}


def get_patient_data(url):
    '''Fetch Patient Data
    Use of requests library to fetch patient related data

    Input: URL
    Output Response: List of patient profiles along with their diet chart, queries and chat history

    '''

    try:
        response = requests.get(url)

        # raise a HTTP Error if the HTTP request returns an unsuccessful status code
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")

    except json.JSONDecodeError as json_err:
        logger.error(f"Error decoding JSON: {json_err}")

    except Exception as err:
        logger.error(f"An error occurred: {err}")

    finally:
        logger.info('successfully fetch for the patient profile')


def search_diet_plan(patient_url, ticket_id, latest_query, chat_history):
    ''' Search patient profile with help of ticket_id

    Parse through whole patient data object to store all the diet and meal information for giving an advice to the query

    Input: Patient URL, Ticket ID, Latest Query, Chat History
    Output: Returns diet related information for all the queries

    '''

    results = []

    # Search for corresponding diet plan
    for query in latest_query:
        for chat in chat_history:
            if chat["message"] == query['content']:
                results.append({
                    "timestamp": chat["timestamp"],
                    "query": query["content"]
                })

    # Get the patient data
    patient_info = get_patient_data(patient_url)
    patient_diet_info = None

    # Search the diet plan by ticket_id
    for patient in patient_info:
        if patient['chat_context']['ticket_id'] == ticket_id:
            patient_diet_info = patient["profile_context"]["diet_chart"]
            break  # Exit loop once the patient is found

    if not patient_diet_info:
        print("No diet plan found for this ticket ID.")
        return

    # Function to parse dates with both formats
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%B %d, %Y, %I:%M %p")
        except ValueError:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

    start_date = patient_diet_info['start_date']

    # Initialize new results list
    new_results = []
    diet_notes = patient_diet_info['notes']
    meal_notes = None
    option_notes = None
    food_names = []
    normal_time = None

    # Function to validate time
    time_format = "%H:%M:%S"

    def validate_time(time_string):
        try:
            time_obj = datetime.strptime(time_string, time_format).time()
            early_morning = datetime.strptime("06:30", "%H:%M").time()
            if time_obj < early_morning:
                raise ValueError("Time cannot be before 06:30")
            return time_obj
        except ValueError as e:
            raise ValueError(f"Invalid time format or value: {e}")

    # Determine the meal type
    # if the user starts a routine early by 10 mins then the routine will be considered as started.
    def get_meal_type(user_time, meal_time_objects):
        grace_period = timedelta(minutes=10)

        # convert the time object into datetime object
        user_time = datetime.combine(datetime.min, user_time)

        sorted_meal_times = sorted(
            meal_time_objects.items(), key=lambda x: datetime.combine(datetime.min, x[1])
        )

        # Convert meal time tuples to datetime
        sorted_meal_times = [(meal, datetime.combine(datetime.min, time))
                             for meal, time in sorted_meal_times]

        if user_time < sorted_meal_times[0][1] - grace_period:
            if user_time >= sorted_meal_times[-1][1]:
                return "post-dinner"
            return "Invalid time"

        for i in range(len(sorted_meal_times) - 1):
            current_meal, current_meal_time = sorted_meal_times[i]
            next_meal, next_meal_time = sorted_meal_times[i + 1]
            if current_meal_time - grace_period <= user_time < next_meal_time - grace_period:
                return current_meal

        return sorted_meal_times[-1][0]

    for query in results:
        # Parse dates
        start_dt = parse_date(start_date).date()
        query_dt = parse_date(query['timestamp']).date()

        # Calculate order number
        order_no = abs((query_dt - start_dt)).days + 1

        # Determine meal type based on time
        date_time = datetime.strptime(
            query['timestamp'], "%B %d, %Y, %I:%M %p")
        user_time = date_time.time()
        meal_type = get_meal_type(user_time, meal_times_objects)

        for diet in patient_diet_info['meals_by_days']:
            if diet['order'] == order_no:
                for meal in diet['meals']:

                    if meal['name'].lower() == meal_type.lower():
                        meal_notes = meal['notes']
                        normal_time = meal['timings']

                        for meal_options in meal['meal_options']:
                            option_notes = meal_options['notes']
                            for items in meal_options['meal_option_food_items']:
                                food_names.append(items['Food']['name'])
                        break
                break

        new_results.append({
            "timestamp": query['timestamp'],
            "normal_time": normal_time,
            "meal_type": meal_type,
            "query": query["query"],
            "order_no": diet['order'],
            "diet_notes": diet_notes,
            "meal_notes": meal_notes,
            "meal_food_options": option_notes,
            "food_names": food_names
        })

        food_names = []

        logging.info(
            "Added all essential details related to query")

    return new_results
