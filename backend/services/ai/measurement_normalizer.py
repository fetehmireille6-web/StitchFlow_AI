import google.generativeai as genai
import json, re, os

synonym_map = {
    "burst": "chest",
    "bust": "chest",
    "full length": "length",
    "back": "back length",
    "shoulder": "back length",
    "waist": "waist",
    "hips": "hips",
    "hip": "hips",
    "hand length": "sleeve",
    "arm length": "sleeve",
}

canonical_fields = ["chest", "length", "back length", "waist", "hips","sleeve", "armhole", "inseam", "outseam", "thigh", "knee", "calf", "ankle"]

def normalize_measurements(text: str):
    text = text.lower()

    # Step 1: Local synonym mapping
    for syn, canonical in synonym_map.items():
        text = text.replace(syn, canonical)

    normalized = {}
    api_key = os.getenv("GEMINI_API_KEY")

    # Step 2: Gemini normalization (only if API key exists)
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are a tailoring assistant. Normalize the following measurements into canonical fields.
            Canonical fields: {canonical_fields}.
            Input: {text}
            Output: Provide ONLY a raw JSON object with canonical field names as keys and numbers as values. No conversation, no markdown blocks.
            """
            response = model.generate_content(prompt)

            # Clean up potential markdown formatting (```json ... ```)
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r'^```(?:json)?\n?|```$', '', raw_text, flags=re.MULTILINE)

            normalized = json.loads(raw_text)
        except Exception as e:
            print(f"AI Normalization skipped or failed: {e}")
            normalized = {}

    # Step 3: Clean values (numbers only)
    cleaned = {}
    for key, value in normalized.items():
        if key in canonical_fields and value is not None:
            match = re.search(r"\d+", str(value))
            if match:
                cleaned[key] = int(match.group(0))

    # Step 4: Fallback if Gemini fails
    if not cleaned:
        for canonical in canonical_fields:
            match = re.search(rf"{canonical} (\d+)", text)
            if match:
                cleaned[canonical] = int(match.group(1))

    return cleaned