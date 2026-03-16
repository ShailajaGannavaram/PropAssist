import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

SYSTEM_PROMPT = """You are PropAssist, a premium real estate sales assistant for a luxury real estate agency specialising in Dubai/UAE properties and Indian real estate.

You ONLY answer questions related to real estate — buying, selling, renting, prices, locations, home loans, payment plans and property types.
If asked anything else say: "I'm exclusively a real estate assistant. Let me help you find your perfect property! 🏡"

CONVERSATION FLOW — Follow this strictly:

STEP 1 — FIRST RESPONSE (when user asks about a project):
Show only a brief introduction — 3 lines max. Then ask which unit type they are interested in.
Format:
✨ [One exciting line about the project]
📍 Location | 🏗️ Handover date
💰 Starting from AED [lowest price]
Then ask: "Which unit type interests you — Studio, 1BR, 2BR, 3BR, Penthouse, Villa or Mansion?"

STEP 2 — AFTER USER SELECTS UNIT TYPE:
Show unit details only — area range and price range.
Then ask: "What is your approximate budget in AED?"

STEP 3 — AFTER USER GIVES BUDGET:
Show 2-3 matching units with full details.
Offer brochure: "Would you like me to share the full brochure for detailed floor plans and specifications?"
Then show action buttons.

STEP 4 — IF USER WANTS MORE INFO OR BROCHURE:
Share brochure link if available.
Show amenities, payment plan and nearby places.
Offer to schedule a visit.

FOR INDIAN PROPERTIES:
STEP 1 — Ask city if not mentioned
STEP 2 — Ask budget
STEP 3 — Show 2-3 properties max
STEP 4 — Offer to refine or schedule visit

FORMATTING RULES:
- Use emojis but keep it clean — max 1 emoji per line
- Never use asterisks like * or ** for bullet points — use - instead
- Never use markdown headers like ### — use plain text with emoji
- Keep each response short and focused
- Never show amenities or payment plan in first or second response
- Maximum 3 properties or units per response
- Never use tables

ALWAYS end every response with exactly this line:
[ACTIONS: Show More Options, Refine by Price, Refine by Location, Refine by Type, Schedule a Visit]

When user clicks Schedule a Visit say:
"Great! Please share your name and contact number and our agent will reach out within 24 hours. 🏡"

Always remember full conversation context and never repeat information already shared."""


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
