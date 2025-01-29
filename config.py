import os
import google.generativeai as genai
import streamlit as st

class AppConfig:
    def __init__(self):
        """
        Loads environment variables from Streamlit secrets and configures the Gemini API.
        """
        self.api_key = st.secrets.get("GEMINI_API_KEY")
        self.sparql_endpoint = st.secrets.get("SPARQL_ENDPOINT", "https://dbpedia.org/sparql")

        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            raise ValueError("Gemini API Key not found in Streamlit secrets.")