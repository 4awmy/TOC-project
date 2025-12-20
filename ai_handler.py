import os
import google.generativeai as genai
import json
import typing
from typing import TypedDict, Optional

class LanguageAnalysis(TypedDict):
    is_regular: bool
    regex: Optional[str]
    explanation: str

class StringCheck(TypedDict):
    accepted: bool
    reason: str

class AIHandler:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            # We will handle missing key gracefully in the UI, but here we can warn or raise
            self.ready = False
        else:
            self.configure_api(api_key)

    def configure_api(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using 'gemini-1.5-flash' for stability and structured output support
        self.model = genai.GenerativeModel('gemini-1.5-flash-001')
        self.ready = True

    def analyze_language(self, description: str) -> dict:
        """
        Analyzes the language description.
        Returns JSON with:
        - is_regular: bool
        - regex: str (or null)
        - explanation: str
        """
        if not self.ready:
            return {"error": "API Key missing"}

        prompt = f"""
        Analyze the following formal language description: "{description}"
        
        Determine if it is a Regular Language.
        If it is Regular, provide a standard Python Regex pattern that matches it.
        If it is NOT Regular, explain why briefly.
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=LanguageAnalysis
                )
            )
            # Response text should be valid JSON matching the schema
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e)}

    def explain_rejection(self, description: str, string: str) -> str:
        """
        Explains why a string is rejected by a Regular language.
        """
        if not self.ready:
            return "API Key missing."

        prompt = f"""
        Language Description: "{description}"
        Test String: "{string}"
        
        The string does NOT match the language. Explain briefly why in one sentence.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error getting explanation: {e}"

    def check_non_regular(self, description: str, string: str) -> dict:
        """
        Checks a string against a non-regular language.
        Returns JSON:
        - accepted: bool
        - reason: str
        """
        if not self.ready:
            return {"error": "API Key missing"}

        prompt = f"""
        Language Description: "{description}"
        Test String: "{string}"
        
        Determine if the string belongs to the language.
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=StringCheck
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e)}
