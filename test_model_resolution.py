import unittest
from unittest.mock import MagicMock
import google.generativeai as genai

# The logic to be tested
def resolve_model_name(available_models):
    """
    Selects the best model from the available_models list.
    available_models: list of objects with a .name attribute.
    """
    # Priority list of models to look for
    # We strip 'models/' prefix for comparison if needed, or check both.
    # Usually list_models returns 'models/gemini-1.5-flash'

    candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro"
    ]

    # Create a set of available model names for O(1) lookup
    # Normalize by removing 'models/' prefix if present
    available_names = set()
    raw_names = {} # Map stripped -> full name

    for m in available_models:
        name = m.name
        if name.startswith("models/"):
            stripped = name[7:]
        else:
            stripped = name
        available_names.add(stripped)
        raw_names[stripped] = name

    # Check candidates
    for candidate in candidates:
        if candidate in available_names:
            return raw_names[candidate]

    # Fallback
    return "gemini-1.5-flash"

class TestModelResolution(unittest.TestCase):
    def make_models(self, names):
        models = []
        for n in names:
            m = MagicMock()
            m.name = n
            m.supported_generation_methods = ["generateContent"]
            models.append(m)
        return models

    def test_exact_match(self):
        models = self.make_models(["models/gemini-1.5-flash", "models/gemini-pro"])
        result = resolve_model_name(models)
        self.assertEqual(result, "models/gemini-1.5-flash")

    def test_variant_match(self):
        models = self.make_models(["models/gemini-1.5-flash-latest", "models/gemini-pro"])
        result = resolve_model_name(models)
        self.assertEqual(result, "models/gemini-1.5-flash-latest")

    def test_fallback_to_pro(self):
        models = self.make_models(["models/gemini-pro", "models/text-bison-001"])
        result = resolve_model_name(models)
        self.assertEqual(result, "models/gemini-pro")

    def test_no_match_fallback(self):
        models = self.make_models(["models/unknown-model"])
        result = resolve_model_name(models)
        self.assertEqual(result, "gemini-1.5-flash")

    def test_empty_list(self):
        models = []
        result = resolve_model_name(models)
        self.assertEqual(result, "gemini-1.5-flash")

    def test_preference_order(self):
        # Should prefer flash over pro
        models = self.make_models(["models/gemini-pro", "models/gemini-1.5-flash"])
        result = resolve_model_name(models)
        self.assertEqual(result, "models/gemini-1.5-flash")

if __name__ == "__main__":
    unittest.main()
