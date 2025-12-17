import re
from ai_handler import AIHandler

class LanguageProcessor:
    def __init__(self):
        self.ai = AIHandler()
        self.current_description = None
        self.is_regular = None
        self.regex = None
        self.analysis_explanation = None

    def set_language(self, description: str):
        self.current_description = description
        if not self.ai.ready:
            # Fallback if no API key: Assume non-regular/manual or just error
            # But for this app, we rely on AI.
            return {"error": "API Key not set"}

        analysis = self.ai.analyze_language(description)
        if "error" in analysis:
            return analysis

        self.is_regular = analysis.get("is_regular", False)
        self.regex = analysis.get("regex")
        self.analysis_explanation = analysis.get("explanation", "")
        
        return analysis

    def process_string(self, string: str):
        if not self.current_description:
            return {"error": "No language defined"}

        if self.is_regular and self.regex:
            # Use Regex
            try:
                match = re.fullmatch(self.regex, string)
                if match:
                    return {
                        "accepted": True,
                        "reason": "Matches regex pattern: " + self.regex
                    }
                else:
                    # Failed regex, ask AI for explanation
                    reason = self.ai.explain_rejection(self.current_description, string)
                    return {
                        "accepted": False,
                        "reason": reason
                    }
            except re.error as e:
                # Fallback if regex is invalid
                return self.ai.check_non_regular(self.current_description, string)
        else:
            # Non-regular or no regex provided
            return self.ai.check_non_regular(self.current_description, string)

    def process_automaton(self, description: str, operation: str):
        if not self.ai.ready:
            return "Error: API Key not set"
        return self.ai.perform_automaton_operation(description, operation)
