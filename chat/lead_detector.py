import re
from .models import Lead


def extract_phone(text):
    pattern = r'(\+91[-\s]?)?[6-9]\d{9}'
    match = re.search(pattern, text.replace(' ', ''))
    if match:
        return match.group()
    return None


def extract_name(text):
    text = text.strip()
    greetings = ['my name is', 'i am', "i'm", 'this is', 'name is']
    for greeting in greetings:
        if greeting in text.lower():
            parts = text.lower().split(greeting)
            if len(parts) > 1:
                name = parts[1].strip().split()[0]
                return name.capitalize()

    words = text.split()
    for word in words:
        if (word[0].isupper() and
            len(word) > 2 and
            word.lower() not in ['show', 'find', 'help', 'want', 'need',
                                  'looking', 'please', 'thanks', 'okay']):
            return word
    return None


def detect_and_save_lead(user_message, session_id, conversation_history):
    phone = extract_phone(user_message)

    if not phone:
        return False

    name = extract_name(user_message)

    if not name:
        for msg in reversed(list(conversation_history)):
            if msg.role == 'user':
                name = extract_name(msg.content)
                if name:
                    break

    interest = ""
    for msg in reversed(list(conversation_history)):
        if msg.role == 'user' and any(
            word in msg.content.lower()
            for word in ['bhk', 'apartment', 'villa', 'house', 'plot',
                        'buy', 'rent', 'looking', 'hyderabad', 'bangalore',
                        'mumbai', 'chennai', 'pune', 'delhi']
        ):
            interest = msg.content[:200]
            break

    if Lead.objects.filter(phone=phone).exists():
        return True

    Lead.objects.create(
        name=name or "Unknown",
        phone=phone,
        interest=interest,
        session_id=session_id
    )
    return True