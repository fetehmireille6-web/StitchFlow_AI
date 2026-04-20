import google.generativeai as genai
import json, re, os
from PIL import Image
import io

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MEASUREMENT_PATTERNS = {
    "neck": r"(?:neck|nk)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "chest": r"(?:chest|bust|burst|b|c)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "waist": r"(?:waist|w)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "hips": r"(?:hips|hip|h)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "shoulder": r"(?:shoulder|s)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "back": r"(?:back|bl)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "front_length": r"(?:front length|fl)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "sleeve": r"(?:sleeve|sl|hand|arm)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "armhole": r"armhole[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "inseam": r"inseam[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "outseam": r"outseam[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "thigh": r"thigh[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "knee": r"knee[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "calf": r"calf[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "ankle": r"ankle[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?",
    "length": r"(?:length|l)[-:=\s]*(\d+(?:\.\d+)?)\s*(?:in|cm|\")?"
}

synonym_map = {
    "full length": "length",
    "back length": "back",
    "back": "back",
    "front length": "front_length",
    "fl": "front_length",
    "waist": "waist",
    "hips": "hips",
    "hip": "hips",
    "l": "length",
    "len": "length",
    "b": "chest",
    "c": "chest",
    "bust": "chest",
    "w": "waist",
    "h": "hips",
    "s": "shoulder",
    "sh": "shoulder",
    "nk": "neck",
    "n": "neck",
    "hand length": "sleeve",
    "arm length": "sleeve",
    "sl": "sleeve",
    "ah": "armhole",
    "th": "thigh",
    "kn": "knee",
}

canonical_fields = ["neck", "chest", "waist", "hips", "shoulder", "back", "front_length", "sleeve", "armhole", "inseam", "outseam", "thigh", "knee", "calf", "ankle", "length"]

def extract_measurements_from_text(text: str):
    """Fallback regex extraction if AI JSON parsing fails."""
    measurements = {}
    for key, pattern in MEASUREMENT_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Extract number from match
                val = matches[0]
                if isinstance(val, tuple): val = val[0]
                num_match = re.search(r'(\d+(?:\.\d+)?)', str(val))
                if num_match:
                    measurements[key] = float(num_match.group(1))
            except (ValueError, TypeError):
                pass
    return measurements

def normalize_measurements(text: str):
    """
    Extracts full order details (customer, garment type, yardage, measurements, due date)
    from the tailor's input using Gemini AI.
    """
    # Default structure to return if AI fails
    result = {
        "customer": "unknown",
        "garment_type": "garment",
        "phone_number": "Not provided",
        "yardage": "0",
        "due_date": "Not specified",
        "measurements": {}
    }

    if api_key:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""
            You are an expert tailoring assistant. Extract structured data from this tailor's order note: "{text}"
            
            Data Extraction Rules:
            - Customer: Name of the person (look for 'Miss', 'Mr', or names after 'for').
            - Garment: Categorize the outfit into one of these styles: 'Senator Suit', 'Agbada (3-piece)', 'Kaftan (Long)', 'Mermaid Gown', 'Ball Gown', 'Dashiki Shirt', or 'Buba & Iro'.
            - Phone: Extract any phone number provided.
            - Date: Extract the due date. NOTE: If provided as DD/MM/YYYY (like 19/04/2026), convert it to YYYY-MM-DD.
            - Measurements: Identify numeric values and map them to these exact keys: {canonical_fields}.
            - Shorthand Mapping:
                - 'nk', 'n' -> neck
                - 'b', 'c', 'bust', 'burst', 'chest' -> chest
                - 'w', 'waist' -> waist
                - 'h', 'hip', 'hips' -> hips
                - 's', 'sh', 'shoulder' -> shoulder
                - 'bl', 'back length', 'back' -> back
                - 'fl', 'front length' -> front_length
                - 'sl', 'hand', 'arm', 'sleeve' -> sleeve
                - 'l', 'len', 'length', 'full length' -> length
                - 'ah', 'armhole' -> armhole
                - 'th', 'thigh' -> thigh
                - 'kn', 'knee' -> knee
            - Important: Be extremely aggressive. If you see a label (even 1-2 letters) followed by a number (e.g., "NK 15", "FL 34", "W: 32"), you MUST extract it.
            
            Output Format (JSON ONLY):
            {{
                "customer": "...",
                "garment_type": "...",
                "phone_number": "...",
                "yardage": "0",
                "due_date": "YYYY-MM-DD",
                "measurements": {{}}
            }}
            Return ONLY a valid JSON object. No markdown.
            """
            # Added safety for non-text inputs or unexpected Gemini responses
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            raw_text = response.text.strip()

            # Robust JSON extraction
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group(0))
                
                # Post-process measurements to match synonym_map
                m_raw = extracted.get("measurements", {})
                m_normalized = {}
                for k, v in m_raw.items():
                    target_k = synonym_map.get(k.lower(), k.lower())
                    if target_k in canonical_fields:
                        m_normalized[target_k] = v
                extracted["measurements"] = m_normalized
                
                result.update(extracted)
        except Exception as e:
            print(f"AI Extraction Error: {e}")

    return result

def normalize_image(image_bytes: bytes, mime_type: str):
    """
    Analyzes a photo using Gemini multimodal AI to extract tailoring details.
    """
    result = {
        "customer": "unknown",
        "garment_type": "garment",
        "phone_number": "Not provided",
        "yardage": "0",
        "due_date": "Not specified",
        "measurements": {}
    }

    if api_key:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            You are an expert tailoring assistant. Carefully examine this image for tailoring details.
            Look for handwritten notes, printed measurement charts, or annotated sketches.
            
            Computer Vision Task:
            1. Reference Object: Look for a standard reference object (Credit Card, A4 Paper, or Ruler) to establish scale.
            2. Keypoint Detection: Identify 2D landmarks (shoulders, chest, waist, hips) for the primary human subject. 
            3. Style Classification: Categorize into 'Senator Suit', 'Agbada (3-piece)', 'Kaftan (Long)', 'Mermaid Gown', 'Ball Gown', 'Dashiki Shirt', or 'Buba & Iro'.
            4. Pose Analysis: Determine if the pose is Frontal or Profile.
            5. Scaling: If a reference object is found, use it to calculate actual cm/inches.
            
            Extraction Task:
            1. Identify and extract measurements for these 16 fields: {canonical_fields}.
            2. Look for handwritten numbers or annotations. 
            3. If no handwritten notes are visible, ESTIMATE measurements based on the subject's body geometry.
            4. Units: Use inches. Convert cm to inches if detected (/2.54).
            
            Output Format (JSON ONLY):
            {{
                "customer": "...",
                "garment_type": "...",
                "phone_number": "...",
                "yardage": "0",
                "measurements": {{}}
            }}
            Return ONLY a valid JSON object. No markdown. No explanations.
            """
            response = model.generate_content([
                {"mime_type": mime_type or "image/jpeg", "data": image_bytes},
                prompt
            ], generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1
            })
            raw_text = response.text.strip()
            
            # Robust JSON match
            json_match = re.search(r'\{[^{}]*"measurements"\s*:\s*\{[^{}]*\}\s*\}', raw_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)

            if json_match:
                extracted = json.loads(json_match.group(0))
                
                # Normalize and filter measurement keys
                m_raw = extracted.get("measurements", {})
                m_normalized = {}
                for k, v in m_raw.items():
                    target_k = synonym_map.get(k.lower(), k.lower())
                    if target_k in canonical_fields:
                        m_normalized[target_k] = v
                extracted["measurements"] = m_normalized
                
                result.update(extracted)
            
            # Fallback: If JSON is empty, try regex on raw text
            if not result["measurements"]:
                result["measurements"] = extract_measurements_from_text(raw_text)

        except Exception as e:
            print(f"AI Image Analysis Error: {e}")

    return result