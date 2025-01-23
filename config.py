import os
from dotenv import load_dotenv
import google.generativeai as genai

class AppConfig:
    def __init__(self, env_file: str = '.env'):
        """
        Loads environment variables from a .env file and configures the Gemini API.
        """
        load_dotenv(env_file)

        self.api_key = os.getenv("GEMINI_API_KEY")
        self.sparql_endpoint = os.getenv("SPARQL_ENDPOINT", "https://dbpedia.org/sparql")

        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            raise ValueError("Gemini API Key not found in environment variables.")
