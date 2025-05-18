from deep_translator import GoogleTranslator

def translate_name(full_name):
    translator = GoogleTranslator(source='ar', target='en')
    parts = translator.translate(full_name).split()
    return parts[0], ' '.join(parts[1:]) if len(parts) > 1 else ""

def translate_text(text):
    return GoogleTranslator(source='ar', target='en').translate(text)

def arabic_to_english_numerals(arabic_str):
    return arabic_str.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789'))
