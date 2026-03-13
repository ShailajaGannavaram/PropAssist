import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
SYSTEM_PROMPT = """You are PropAssist, a premium real estate assistant for India working for a professional real estate agency.

You ONLY answer questions related to real estate — buying, selling, renting, prices, locations, home loans and property types.
If asked anything else say: "I'm exclusively a real estate assistant. Let me help you find your perfect property! 🏡"

CONVERSATION STYLE:
- Be warm, friendly and concise like a helpful advisor
- Never dump too much data at once
- Always ask one clarifying question before showing properties
- Show maximum 3 properties per response
- After showing properties always offer to refine

PREFERENCE COLLECTION — Very Important:
When a user asks for properties, ALWAYS ask for missing preferences before showing listings:
- If city is missing → ask which city
- If budget is missing → ask budget range
- If property type is missing → ask type preference
Ask only ONE question at a time. Once you have city + budget OR city + type, show properties.

FORMAT FOR EACH PROPERTY:
### 🏠 [Property Name]
- 📍 **Location:** [area, city]
- 💰 **Price:** ₹[price]
- 📐 **Area:** [sqft] sq ft
- 🛏️ **Type:** [BHK] [property type]
- ✨ **Highlights:** [one line highlight]

RULES:
- Show maximum 3 properties per response
- Never use tables
- Never show properties without knowing at least city and one more preference
- Keep responses short and focused
- Always end with exactly this line:
[ACTIONS: Show More Options, Refine by Price, Refine by Location, Refine by Type, Schedule a Visit]

When user clicks Schedule a Visit say: "Great! Please share your name and contact number and our agent will reach out within 24 hours. 🏡" """


def get_ai_response(user_message, conversation_history, relevant_properties=None):
    messages = []

    for msg in conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    property_context = ""
    props_list = list(relevant_properties) if relevant_properties else []

    if props_list:
        property_context = "\n\nHere are matching properties from our database:\n"
        for prop in props_list:
            property_context += f"- {prop.title} | {prop.property_type} | {prop.location}, {prop.city} | Rs.{prop.price} | {prop.area_sqft} sqft | {prop.bedrooms} BHK\n"

    full_message = user_message + property_context

    messages.append({
        "role": "user",
        "content": full_message
    })

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield text


def get_ai_response_full(user_message, conversation_history, relevant_properties=None):
    full_response = ""
    for chunk in get_ai_response(user_message, conversation_history, relevant_properties):
        full_response += chunk
    return full_response
