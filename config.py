import os
import google.generativeai as genai
import openai
import streamlit as st

class AppConfig:
    def __init__(self):
        """
        Loads environment variables from Streamlit secrets and configures the Gemini and OpenAI APIs.
        """
        self.gemini_api_key = st.secrets.get("GEMINI_API_KEY")
        self.openai_api_key = st.secrets.get("OPENAI_API_KEY")
        self.endpoint = "https://dbpedia.org/sparql"  # Set SPARQL endpoint directly

        self.api_key = st.secrets.get("GEMINI_API_KEY")
        self.default_sparql_endpoint = "https://dbpedia.org/sparql"  # Default SPARQL endpoint

        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
        else:
            raise ValueError("Gemini API Key not found in Streamlit secrets.")

        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            raise ValueError("OpenAI API Key not found in Streamlit secrets.")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)