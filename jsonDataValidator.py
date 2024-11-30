import json
from typing import Any, Dict

class JSONValidator:
    def __init__(self, template: Dict[str, Any], data: Dict[str, Any]):
        self.template = template
        self.data = data
        self.validate()

    def validate(self):
        """Validates the data against the template."""
        for key, expected_type in self.template.items():
            if key not in self.data:
                raise KeyError(f"Missing key: {key}")
            if not isinstance(self.data[key], expected_type):
                raise TypeError(f"Incorrect type for key '{key}': expected {expected_type.__name__}, got {type(self.data[key]).__name__}")

    def is_valid(self) -> bool:
        """Returns True if the data is valid, False otherwise."""
        try:
            self.validate()
            return True
        except (KeyError, TypeError):
            return False


# Example usage
if __name__ == "__main__":
    # Define a template for the expected JSON structure
    template = {
        "width": int,
        "height": int,
        "bounding_boxes": list
    }

    # Load data from JSON
    with open("data.json", "r") as f:
        json_data = json.loads(f.read())

    # Create a JSONValidator instance
    validator = JSONValidator(template, json_data)

    # Check if the data is valid
    if validator.is_valid():
        print("Data is valid.")
    else:
        print("Data is invalid.")
