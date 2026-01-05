import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logging.warning("OPENAI_API_KEY not found. LLM features will be disabled or mocked.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def get_completion(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Generates completion from LLM.
        """
        if not self.client:
            return "LLM API Key missing. Insight generation skipped."
            
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error calling LLM: {e}")
            return "Error generating insights."
