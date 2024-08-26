import cohere
import openai
import google.generativeai as genai
import os


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
