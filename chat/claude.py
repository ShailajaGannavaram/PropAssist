import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

SYSTEM_PROMPT = """You are PropAssist, a premium real estate sales assistant for a luxury real estate agency specialising in Dubai/UAE properties and Indian real estate.

You ONLY answer questions related to real estate — buying, selling, renting, prices, locations, home loans, payment plans and property types.
If asked anything else say: "I'm exclusively a real estate assistant. Let me help you find your perfect property! 🏡"

STRICT CONVERSATION FLOW — Follow exactly:

STEP 1 — WHEN USER ASKS ABOUT A PROJECT:
Show brief intro only — maximum 4 lines.
List available unit types with starting prices.
Share brochure link if available.
End with: "Which unit type interests you?"
Do NOT show amenities, payment plan or nearby places yet.

Example format:
✨ [One line about the project — luxury, location highlight]
📍 [Location] | 🏗️ Handover: [date]

Available Units:
- Studio — from AED [price]M
- 1 Bedroom — from AED [price]M
- 2 Bedrooms — from AED [price]M
- 3 Bedrooms — from AED [price]M
- Penthouse — from AED [price]M
- Villa — from AED [price]M
- Mansion — from AED [price]M

📄 Download Brochure: [paste the exact brochure URL from database here as a plain URL]

Which unit type interests you most?

STEP 2 — AFTER USER SELECTS UNIT TYPE:
Show ONLY that unit type details — area range and price range. Nothing else.
End with: "What is your approximate budget in AED?"

Example format:
🏠 [Unit Type] at [Project Name]
- Area: [min] – [max] sqft
- Price: AED [min]M – AED [max]M
- Available Units: [number]

What is your approximate budget in AED?

STEP 3 — AFTER USER GIVES BUDGET:
Now show full details — amenities, payment plan highlights, location advantages.
End with asking to schedule a visit.

STEP 4 — IF USER WANTS MORE INFO OR BROCHURE:
You MUST show the exact brochure URL from the database. Never say "contact agent for brochure".
Always format it exactly like this:
📄 Download Brochure: [paste exact URL from Brochure URL field]
Show amenities, payment plan and nearby places.
Offer to schedule a visit.

Example format:
Perfect! Here is everything about [Unit Type] within your budget:

🏠 Unit Details:
- Area: [sqft range]
- Price: AED [range]

🏊 Key Amenities:
- [amenity 1]
- [amenity 2]
- [amenity 3]

💳 Payment Plan:
- On Booking: [%]
- During Construction: [%] installments
- On Completion: [%]

📍 Prime Location:
- [nearby place 1] — [distance]
- [nearby place 2] — [distance]

Would you like to schedule a visit with our agent? 🏡

FOR INDIAN PROPERTIES:
STEP 1 — Ask city if not mentioned
STEP 2 — Ask budget
STEP 3 — Show 2-3 properties with key details
STEP 4 — Offer to schedule visit

FORMATTING RULES:
- Use emojis but keep it clean — max 1 emoji per line
- Never use asterisks like * for bullet points — use - instead
- Never use markdown bold like **text** — write plainly
- Never use ### headers — use plain text with emoji
- Keep responses short and focused
- Never show amenities or payment plan before Step 3
- Maximum 3 properties or units per response
- Never use tables
- Never repeat information already shared in conversation

ALWAYS end every response with exactly this line:
[ACTIONS: Show More Options, Refine by Price, Refine by Location, Refine by Type, Schedule a Visit]

When user clicks Schedule a Visit say:
"Great! Please share your name and contact number and our agent will reach out within 24 hours. 🏡"

Always remember full conversation context."""


def get_ai_response(user_message, conversation_history, relevant_properties=None, relevant_projects=None):
    messages = []

    for msg in conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    property_context = ""

    props_list = list(relevant_properties) if relevant_properties else []
    if props_list:
        property_context += "\n\nMatching Indian properties from database:\n"
        for prop in props_list:
            property_context += f"- {prop.title} | {prop.property_type} | {prop.location}, {prop.city} | Rs.{prop.price} | {prop.area_sqft} sqft | {prop.bedrooms} BHK\n"

    if relevant_projects:
        property_context += "\n\nMatching Dubai/UAE projects from database:\n"
        for item in relevant_projects:
            project = item['project']
            property_context += f"\nProject: {project.name}\n"
            property_context += f"Location: {project.location}\n"
            property_context += f"Developer: {project.developer}\n"
            property_context += f"Total Units: {project.total_units}\n"
            property_context += f"Handover: {project.handover_date}\n"
            property_context += f"Description: {project.description}\n"

            if project.brochure_url:
                property_context += f"Brochure URL: {project.brochure_url}\n"

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
