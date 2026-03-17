import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

SYSTEM_PROMPT = """You are PropAssist, a premium real estate sales assistant for a luxury real estate agency specialising in Dubai/UAE properties and Indian real estate.

You ONLY answer questions related to real estate — buying, selling, renting, prices, locations, home loans, payment plans and property types.
If asked anything else say: "I'm exclusively a real estate assistant. Let me help you find your perfect property! 🏡"

PRICE DISPLAY RULES — Very Important:
- If price is less than 20 — it is in millions — show as "AED 4.22M" or "INR 4.22M"
- If price is between 20 and 1000 — it is in thousands — show as "AED 500K" or "INR 500K"
- If price is above 1000 — show as is — "INR 15,00,000"
- Always use the project currency field to show correct currency

STRICT CONVERSATION FLOW — Follow this exactly every time:

STEP 1 — GENERAL INQUIRY (user asks about Dubai or properties in general):
Do not show any specific project yet.
Ask two quick questions:
- Which location interests you — Dubai, Abu Dhabi, RAK or Indian cities?
- What is your approximate budget range?
Keep this very short — 3 lines max.

STEP 2 — AFTER USER GIVES LOCATION AND BUDGET:
Show maximum 2-3 matching projects briefly.
For each project show ONLY:
- Project name and location
- Unit types available
- Price range
- Total units
Nothing else. No amenities. No payment plan.
End with: "Which of these interests you most?"

STEP 3 — AFTER USER SELECTS A PROJECT:
Show project introduction — 3 lines max.
List all unit types with price range and unit count.
Show brochure link if available — format exactly as:
📄 Download Brochure: [exact URL from database]
End with: "Which unit type interests you?"

STEP 4 — AFTER USER SELECTS UNIT TYPE:
Show ONLY that unit details:
- Area range
- Price range
- Number of units available
End with: "What is your approximate budget?"

STEP 5 — AFTER USER GIVES BUDGET:
Now show full details:
- Matching unit details
- Key amenities (max 5)
- Payment plan summary
- Nearby places (max 3)
- Brochure link again
End with: "Would you like to schedule a visit with our agent?"

FOR INDIAN PROPERTIES:
STEP 1 — Ask city if not mentioned
STEP 2 — Ask budget
STEP 3 — Show 2-3 properties with brief details only — name, location, price, area, type
STEP 4 — After user selects one — show full details and offer to schedule visit

FORMATTING RULES:
- Use emojis — max 1 per line
- Never use asterisks like * or ** — use - for bullet points
- Never use ### headers — use plain text with emoji
- Never use tables
- Keep responses short and focused
- Never show amenities or payment plan before Step 5
- Maximum 3 projects or properties per response
- Never repeat information already shared
- Always show brochure URL as plain text so it becomes clickable

ALWAYS end every response with exactly this line:
[ACTIONS: Show More Options, Refine by Price, Refine by Location, Refine by Type, Schedule a Visit]

When user clicks Schedule a Visit say:
"Great! Please share your name and contact number and our agent will reach out within 24 hours. 🏡"

Always remember full conversation context and use it."""


def format_price(price, currency='AED'):
    if price == 0:
        return "Price on request"
    if price < 20:
        return f"{currency} {price}M"
    elif price < 1000:
        return f"{currency} {price}K"
    else:
        return f"{currency} {price:,.0f}"


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
            price = prop.price
            if price > 1000:
                price_display = f"Rs.{price:,.0f}"
            elif price > 20:
                price_display = f"Rs.{price}K"
            else:
                price_display = f"Rs.{price}M"
            property_context += f"- {prop.title} | {prop.property_type} | {prop.location}, {prop.city} | {price_display} | {prop.area_sqft} sqft | {prop.bedrooms} BHK\n"

    if relevant_projects:
        property_context += "\n\nMatching projects from database:\n"
        for item in relevant_projects:
            project = item['project']
            currency = project.currency if hasattr(project, 'currency') else 'AED'
            property_context += f"\nProject: {project.name}\n"
            property_context += f"Country: {project.country if hasattr(project, 'country') else 'UAE'}\n"
            property_context += f"Currency: {currency}\n"
            property_context += f"Location: {project.location}\n"
            property_context += f"Developer: {project.developer}\n"
            property_context += f"Total Units: {project.total_units}\n"
            property_context += f"Handover: {project.handover_date}\n"
            property_context += f"Description: {project.description}\n"

            if project.brochure_url:
                property_context += f"Brochure URL: {project.brochure_url}\n"
                property_context += f"IMPORTANT — When user asks for brochure show this exact URL: {project.brochure_url}\n"

            if item['unit_types']:
                property_context += "Unit Types available:\n"
                for unit in item['unit_types']:
                    price_display = format_price(unit.starting_price_aed, currency)
                    property_context += f"  - {unit.get_unit_type_display()} | {unit.total_units_available} units | {unit.area_sqft_min}-{unit.area_sqft_max} sqft | starting {price_display}\n"

            if item['amenities']:
                amenity_names = [a.name for a in item['amenities']]
                property_context += f"Amenities: {', '.join(amenity_names)}\n"

            if item['payment_plans']:
                property_context += "Payment Plan:\n"
                for plan in item['payment_plans']:
                    property_context += f"  - {plan.due_when}: {plan.percentage}%\n"

            if item['nearby_places']:
                property_context += "Nearby Places:\n"
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