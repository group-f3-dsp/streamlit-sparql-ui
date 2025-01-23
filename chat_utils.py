import google.generativeai as genai
import re

class ChatManager:
    """
    A simple class to manage chat messages and interact with the Gemini model.
    """

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.messages = []
        self.model = genai.GenerativeModel(model_name)

    def add_user_message(self, message: str):
        """
        Adds a user message to the conversation history.
        """
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str):
        """
        Adds an assistant (bot) message to the conversation history.
        """
        self.messages.append({"role": "assistant", "content": message})

    def generate_response(self, prompt: str) -> str:
        """
        Uses the configured model to generate content.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def get_conversation(self):
        """
        Returns the conversation history.
        """
        return self.messages

    def extract_sparql_query(self, text: str) -> str:
        """
        Attempt to extract only the SPARQL query from a chunk of text,
        ignoring any explanations or extra commentary. 
        1) Prefer a fenced code block with ```sparql ...
        2) Fallback: find the first mention of SELECT, ASK, or CONSTRUCT
           and capture until the end of the text.
        """
        code_blocks = re.findall(r"```(?:sparql)?(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if code_blocks:
            return code_blocks[0].strip()

        match = re.search(r"(?i)(SELECT|ASK|CONSTRUCT)\s.*", text, re.DOTALL)
        if match:
            raw_query = match.group(0)
            raw_query = re.sub(r"```+", "", raw_query)
            return raw_query.strip()

        return ""
