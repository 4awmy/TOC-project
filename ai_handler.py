import os
import google.generativeai as genai
import json
import typing
from typing import TypedDict, Optional
import logging

logger = logging.getLogger(__name__)

class LanguageAnalysis(TypedDict):
    is_regular: bool
    regex: Optional[str]
    explanation: str

class StringCheck(TypedDict):
    accepted: bool
    reason: str

class AIHandler:
    def __init__(self):
        self.model_name = "gemini-1.5-flash" # Default
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            # We will handle missing key gracefully in the UI, but here we can warn or raise
            self.ready = False
        else:
            self.configure_api(api_key)

    def _resolve_model_name(self) -> str:
        """
        Dynamically finds the best available model name to avoid 404 errors.
        """
        try:
            logger.info("Listing available models...")
            # List models and filter for those that support generateContent
            available_models = list(genai.list_models())

            candidates = [
                "gemini-1.5-flash",
                "gemini-1.5-flash-latest",
                "gemini-1.5-flash-001",
                "gemini-flash-latest",
                "gemini-1.5-pro",
                "gemini-pro"
            ]

            available_names = set()
            raw_names = {}

            for m in available_models:
                if "generateContent" in m.supported_generation_methods:
                    name = m.name
                    # Usually 'models/gemini-1.5-flash'
                    if name.startswith("models/"):
                        stripped = name[7:]
                    else:
                        stripped = name

                    available_names.add(stripped)
                    raw_names[stripped] = name

            logger.info(f"Available models: {list(available_names)}")

            for candidate in candidates:
                if candidate in available_names:
                    selected = raw_names[candidate]
                    logger.info(f"Selected model: {selected}")
                    return selected

            # Fallback if no candidates match
            logger.warning("No preferred model found. Falling back to default.")
            return "gemini-1.5-flash"

        except Exception as e:
            logger.error(f"Error listing models: {e}. using default.")
            return "gemini-1.5-flash"

    def configure_api(self, api_key: str):
        genai.configure(api_key=api_key)

        # Resolve model name dynamically
        self.model_name = self._resolve_model_name()

        # Initialize model
        self.model = genai.GenerativeModel(self.model_name)
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
            return {"error": f"Error with model {self.model_name}: {str(e)}"}

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
