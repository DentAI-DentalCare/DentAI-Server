import json, re, unicodedata, os
from services.translate_service import translate_text, translate_name, arabic_to_english_numerals
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read the GROQ API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def clean_text(text):
    return re.sub(r'[^A-Za-z0-9\s]', '', text)

def extract_json_from_string(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None

def handle_special_cases(text, ai_msg_content):
    if ai_msg_content is None:
        return {"error": "Unable to connect to the server"}
    
    print("AI Response:", ai_msg_content)

    # Attempt to parse JSON directly
    try:
        ai_msg_dict = json.loads(ai_msg_content)
    except Exception:
        # Try extracting JSON from the content using regex
        json_str = extract_json_from_string(ai_msg_content)
        if not json_str:
            return {"error": "Failed to parse AI response"}
        try:
            ai_msg_dict = json.loads(json_str)
        except Exception:
            return {"error": "Still failed to parse JSON"}

    if not all(k in ai_msg_dict for k in ["firstName", "lastName", "streetAddress", "city", "nationalId"]):
        return {"error": "No national ID information found"}

    national_id = ''.join(c for c in ai_msg_dict["nationalId"] if c.strip())

    def normalize_arabic_digits(nid):
        return ''.join(arabic_to_english_numerals(c) if not c.isdigit() else c for c in nid)

    national_id = arabic_to_english_numerals(''.join(c for c in ai_msg_dict["nationalId"] if c.strip()))

    print("Normalized National ID:", national_id)

    if len(national_id) != 14 or not national_id.isdigit():
        return {"error": "National ID is incorrect"}

    birth_year = national_id[1:3]
    birth_month = national_id[3:5]
    birth_day = national_id[5:7]
    century = national_id[0]
    birth_year = arabic_to_english_numerals(("19" if century == "2" else "20") + birth_year)
    birth_month = arabic_to_english_numerals(birth_month)
    birth_day = arabic_to_english_numerals(birth_day)

    gender_digit = int(national_id[12])
    gender = "male" if gender_digit % 2 else "female"

    first_name, last_name = translate_name(f"{ai_msg_dict['firstName']} {ai_msg_dict['lastName']}")
    return {
        "firstName": clean_text(first_name),
        "lastName": clean_text(last_name),
        "streetAddress": translate_text(ai_msg_dict["streetAddress"]),
        "city": translate_text(ai_msg_dict["city"]),
        "nationalId": national_id,
        "birthday": f"{birth_day}-{birth_month}-{birth_year}",
        "gender": gender,
    }

# Use a strong instruction to return only JSON
messages = [{
    "role": "system",
    "content": "You are an assistant that extracts national ID info. ONLY respond with a valid JSON object like: { \"firstName\":..., \"lastName\":..., \"streetAddress\":..., \"city\":..., \"nationalId\":... }. Do not explain. No extra text. No greeting."
}]

def get_national_id_info(id_text):
    messages.append({"role": "user", "content": id_text})
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0
        )
        ai_msg = response.choices[0].message.content
    except Exception as e:
        print("Groq Error:", e)
        ai_msg = None

    result = handle_special_cases(id_text, ai_msg)
    if "error" not in result:
        messages.append({"role": "assistant", "content": ai_msg})
    return result
