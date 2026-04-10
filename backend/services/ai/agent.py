import re
from datetime import datetime, timedelta
from services.ai.measurement_normalizer import normalize_measurements

class StitchFlowAgent:
    def __init__(self):
        self.measurement_patterns = {
            "neck": r"neck (\d+)",
            "chest": r"chest (\d+)",
            "waist": r"waist (\d+)",
            "hips": r"hips (\d+)",
            "shoulder": r"shoulder (\d+)",
            "back": r"back length (\d+)",
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

    def parse_command(self, text: str):
        text = text.lower()
        name_match = re.search(r"for (\w+)", text)
        customer = name_match.group(1) if name_match else "unknown"

        # Step 1: Try Gemini-powered normalization (handles synonyms like 'bust' -> 'chest')
        measurements = normalize_measurements(text)

        # Step 2: Fallback to local regex patterns if AI found nothing
        if not measurements:
            for key, pattern in self.measurement_patterns.items():
                match = re.search(pattern, text)
                if match:
                    measurements[key] = match.group(1)

        return {
            "customer": customer,
            "measurements": measurements,
            "intent": "new_order" if "new" in text else "query"
        }
    def calculate_yardage(self, measurements: dict):
        # Example: yardage = chest + length / some factor
        return int(measurements.get("chest", 0)) + int(measurements.get("length", 0))

    def notify_due_date(self, due_date: str):
        # Example: check if today == due_date - 1
        today = datetime.today().date()
        dd = datetime.strptime(due_date, "%Y-%m-%d").date()
        if today == dd - timedelta(days=1):
            return "Reminder: fitting tomorrow!"
        return None
