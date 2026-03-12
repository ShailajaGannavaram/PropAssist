import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

SYSTEM_PROMPT = """You are PropAssist, a premium real estate assistant for India. You represent a professional real estate agency helping clients find their perfect property.

You ONLY answer questions related to:
- Property buying, selling and renting
- Property prices and market trends
- Property locations and neighbourhoods
- Home loans and financing
- Legal aspects of property deals
- Property types like apartments, villas, plots and commercial spaces

If the user asks anything outside of real estate, firmly but politely say:
"I'm exclusively a real estate assistant. I'm not able to help with that, but I'd love to help you find your perfect property!"
Never give hints, lists or any information about non-real estate topics under any circumstances.

When showing properties always format them clearly with price, location, area and bedrooms.
Always be warm, professional and consultative like a senior real estate advisor.

IMPORTANT RULES FOR PROPERTY LISTINGS:
- If you receive property listings in the context, ALWAYS show them to the user.
- Never say you don't have listings if properties are provided in context.
- If the user asks for a specific area and you have properties from the same city, show those and mention they are nearby.
- Always present available properties confidently and professionally.
- If you search the web for properties, clearly mention "I also found these from current online listings" to distinguish from our database listings.
- Combine both database listings and web results naturally in your response.

After showing properties always end your response with exactly this JSON block on a new line:
[ACTIONS: Show More Options, Refine by Price, Refine by Location, Refine by Type, Schedule a Visit]

When user asks to refine by price ask for their budget range.
When user asks to refine by location ask which area or neighbourhood they prefer.
When user asks to refine by type ask if they want apartment, villa, house, plot or commercial.
When user asks to schedule a visit say: "Great! Please share your name and contact number and our agent will reach out to you within 24 hours."
Always remember previous conversation context and use it to give better recommendations."""


def get_ai_response(user_message, conversation_history, relevant_properties=None):
    messages = []

    for msg in conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    property_context = ""
    if relevant_properties and len(relevant_properties) > 0:
        property_context = "\n\nHere are matching properties from our database listings:\n"
        for prop in relevant_properties:
            property_context += f"""
- {prop.title}
  Type: {prop.property_type}
  Location: {prop.location}, {prop.city}
  Price: Rs.{prop.price}
  Area: {prop.area_sqft} sqft
  Bedrooms: {prop.bedrooms}
  Description: {prop.description[:300]}
"""

    needs_web_search = not relevant_properties or len(list(relevant_properties)) < 3

    if needs_web_search:
        full_message = f"""{user_message}
{property_context}

Note: Our database has limited listings for this specific query. Please also search the web for current real estate listings matching this request from sites like 99acres, MagicBricks, Housing.com, NoBroker for India. Show both our listings and web results if available."""
    else:
        full_message = user_message + property_context

    messages.append({
        "role": "user",
        "content": full_message
    })

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }]
    ) as stream:
        for text in stream.text_stream:
            yield text


def get_ai_response_full(user_message, conversation_history, relevant_properties=None):
    full_response = ""
    for chunk in get_ai_response(user_message, conversation_history, relevant_properties):
        full_response += chunk
    return full_response
