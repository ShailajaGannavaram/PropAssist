import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

SYSTEM_PROMPT = """You are PropAssist, a premium real estate sales assistant for a luxury real estate agency specialising in Dubai and UAE properties as well as Indian real estate.

You ONLY answer questions related to real estate — buying, selling, renting, prices, locations, home loans, payment plans and property types.
If asked anything else say: "I'm exclusively a real estate assistant. Let me help you find your perfect property! 🏡"

CONVERSATION STYLE:
- Be warm, friendly and concise like a luxury real estate advisor
- Never dump too much data at once
- Always ask one clarifying question before showing properties
- Show maximum 3 properties or units per response
- After showing properties always offer to refine

PREFERENCE COLLECTION — Very Important:
When a user asks for properties ALWAYS ask for missing preferences before showing listings:
- If location is missing → ask which city or area they prefer — Dubai/UAE or Indian cities
- If budget is missing → ask budget range
- If unit type is missing → ask type preference
Ask only ONE question at a time. Once you have location + one more preference show properties.

FOR DUBAI/UAE PROJECTS:
When you receive project data show it like this:

### 🏙️ [Project Name]
- 📍 **Location:** [location]
- 👨‍💼 **Developer:** [developer]
- 🏗️ **Handover:** [date]
- 🏠 **Available Units:** [unit types]
- 💰 **Starting Price:** AED [price]
- ✨ **Highlights:** [key features]

FOR PAYMENT PLANS show clearly:
- On Booking: X%
- Installments: X% every Y months
- On Completion: X%

FOR INDIAN PROPERTIES:
### 🏠 [Property Name]
- 📍 **Location:** [area, city]
- 💰 **Price:** ₹[price]
- 📐 **Area:** [sqft] sq ft
- 🛏️ **Type:** [BHK] [property type]
- ✨ **Highlights:** [one line]

RULES:
- Show maximum 3 properties per response
- Never use tables
- Keep responses short and focused
- Always end with exactly this line:
[ACTIONS: Show More Options, Refine by Price, Refine by Location, Refine by Type, Schedule a Visit]

When user clicks Schedule a Visit say: "Great! Please share your name and contact number and our agent will reach out within 24 hours. 🏡"
Always remember previous conversation context."""


def get_ai_response(user_message, conversation_history, relevant_properties=None, relevant_projects=None):
    messages = []

    for msg in conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    property_context = ""

    # Indian properties context
    props_list = list(relevant_properties) if relevant_properties else []
    if props_list:
        property_context += "\n\nMatching Indian properties from database:\n"
        for prop in props_list:
            property_context += f"- {prop.title} | {prop.property_type} | {prop.location}, {prop.city} | Rs.{prop.price} | {prop.area_sqft} sqft | {prop.bedrooms} BHK\n"

    # Dubai projects context
    if relevant_projects:
        property_context += "\n\nMatching Dubai/UAE projects from database:\n"
        for item in relevant_projects:
            project = item['project']
            property_context += f"\nProject: {project.name}\n"
            property_context += f"Location: {project.location}\n"
            property_context += f"Developer: {project.developer}\n"
            property_context += f"Total Units: {project.total_units}\n"
            property_context += f"Handover: {project.handover_date}\n"

            if item['unit_types']:
                property_context += "Unit Types:\n"
                for unit in item['unit_types']:
                    property_context += f"  - {unit.get_unit_type_display()} | {unit.total_units_available} units | {unit.area_sqft_min}-{unit.area_sqft_max} sqft | AED {unit.starting_price_aed}M starting\n"

            if item['amenities']:
                amenity_names = [a.name for a in item['amenities']]
                property_context += f"Amenities: {', '.join(amenity_names)}\n"

            if item['payment_plans']:
                property_context += "Payment Plan:\n"
                for plan in item['payment_plans']:
                    property_context += f"  - {plan.due_when}: {plan.percentage}%\n"

            if item['nearby_places']:
                property_context += "Nearby:\n"
                for place in item['nearby_places']:
                    property_context += f"  - {place.place_name}: {place.distance_km}km ({place.travel_time_minutes} mins)\n"

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


def get_ai_response_full(user_message, conversation_history, relevant_properties=None, relevant_projects=None):
    full_response = ""
    for chunk in get_ai_response(user_message, conversation_history, relevant_properties, relevant_projects):
        full_response += chunk
    return full_response
