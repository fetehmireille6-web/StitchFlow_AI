import re

class StitchFlowAgent:
    def __init__(self):
        self.measurement_patterns = {
            "neck": r"neck (\d+)",
            "chest": r"chest (\d+)",
            "waist": r"waist (\d+)",
            "hips": r"hips (\d+)",
            "shoulder": r"shoulder (\d+)",
            "back_length": r"back length (\d+)",
            "front_length": r"front length (\d+)",
            "sleeve": r"sleeve (\d+)",
            "armhole": r"armhole (\d+)",
            "inseam": r"inseam (\d+)",
            "outseam": r"outseam (\d+)",
            "thigh": r"thigh (\d+)",
            "knee": r"knee (\d+)",
            "calf": r"calf (\d+)",
            "ankle": r"ankle (\d+)",
            "length": r"length (\d+)"
        }

    def parse_command(self, text):
        text = text.lower()
        name_match = re.search(r"for (\w+)", text)
        customer = name_match.group(1) if name_match else "unknown"

        measurements = {}
        for key, pattern in self.measurement_patterns.items():
            match = re.search(pattern, text)
            if match:
                measurements[key] = match.group(1)

        return {
            "customer": customer,
            "measurements": measurements,
            "intent": "new_order" if "new" in text else "query"
        }