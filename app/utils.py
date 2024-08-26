import cohere
import openai
import google.generativeai as genai
import os
import logging
import json


def get_client(llm):
    ''' Initialize LLM Client

    Using the base models of LLMs: OpenAI, Google Gemini, Cohere

    '''
    if llm.startswith("gpt"):
        base_url = os.environ["OPENAI_API_BASE"]
        api_key = os.environ["OPENAI_API_KEY"]
        client = openai.OpenAI(base_url=base_url, api_key=api_key)

    elif llm.startswith("gemini"):
        api_key = os.environ["GOOGLE_GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        client = genai.GenerativeModel(llm)

    else:
        # For Cohere
        api_key = os.environ["COHERE_API_KEY"]
        client = cohere.Client(api_key=api_key)

    return client


def generate_response(llm, message):
    try:
        client = get_client(llm)

        logging.info("Starting LLM API call")

        if llm.startswith("gpt"):
            logging.info("Invoking gpt LLM API")
            response = client.completions.create(
                engine='text-davinci-002',
                prompt=message,
                max_tokens=4096
            )

            logging.info("GPT API call successful")

            response_text = response.choices[0].text.strip()

        elif llm.startswith("gemini"):
            logging.info("Invoking gemini LLM API")

            response = client.generate_content(message)

            logging.info("Gemini API call successful")
            response_text = response.text.strip()

        else:  # Cohere
            logging.info("Invoking cohere LLM API")

            chat_completion = client.chat(
                model=llm,
                max_tokens=4092,
                temperature=0.8,
                message=message,
            )

            logging.info("Cohere API call successful")
            response_text = chat_completion.text.strip()

        # Attempt to parse the LLM response as JSON
        try:
            response_json = json.loads(response_text)
            return response_json
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing LLM response as JSON: {e}")
            # Return the raw response text and an error message in JSON format
            return {
                "error": "Invalid JSON format in LLM response",
                "raw_response": response_text
            }

    except Exception as e:
        logging.error(f"Exception in generate_response: {e}")
        return None
