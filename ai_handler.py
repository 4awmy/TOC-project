import os
import google.generativeai as genai
import json
import typing

class AIHandler:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            # We will handle missing key gracefully in the UI, but here we can warn or raise
            self.ready = False
        else:
            genai.configure(api_key=api_key)
            # Using 'gemini-flash-latest' as it was verified to work in this environment
            # where 'gemini-1.5-flash' returned a 404 error.
            self.model = genai.GenerativeModel('gemini-flash-latest')
            self.ready = True

    def _get_json_response(self, prompt: str) -> dict:
        if not self.ready:
            return {"error": "API Key missing"}
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e)}

    def analyze_language(self, description: str) -> dict:
        """
        Analyzes the language description.
        Returns JSON with:
        - is_regular: bool
        - regex: str (or null)
        - explanation: str
        """
        prompt = f"""
        Analyze the following formal language description: "{description}"
        
        Determine if it is a Regular Language.
        If it is Regular, provide a standard Python Regex pattern that matches it.
        If it is NOT Regular, explain why briefly.
        
        Output valid JSON with this schema:
        {{
            "is_regular": boolean,
            "regex": "string or null (use valid python regex syntax, e.g. ^...$)",
            "explanation": "string explaining the reasoning"
        }}
        Do NOT wrap the output in markdown code blocks. Return raw JSON only.
        """
        return self._get_json_response(prompt)

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
        prompt = f"""
        Language Description: "{description}"
        Test String: "{string}"
        
        Determine if the string belongs to the language.
        
        Output valid JSON with this schema:
        {{
            "accepted": boolean,
            "reason": "string explaining why it is accepted or rejected"
        }}
        Do NOT wrap the output in markdown code blocks. Return raw JSON only.
        """
        return self._get_json_response(prompt)
