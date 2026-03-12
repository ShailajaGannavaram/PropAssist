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
Keep your responses concise. Show maximum 5 properties per response. Be brief and professional.

IMPORTANT RULES FOR PROPERTY LISTINGS:
- If you receive property listings in the context, ALWAYS show them to the user.
- Never say you don't have listings if properties are provided in context.
- If the user asks for a specific area and you have properties from the same city, show those and mention they are nearby.
- Always present available properties confidently and professionally.
- If web search results are provided combine them naturally with database listings.

IMPORTANT: Always end EVERY response with this exact line:
[ACTIONS: Show More Options, Refine by Price, Refine by Location, Refine by Type, Schedule a Visit]

When user asks to refine by price ask for their budget range.
When user asks to refine by location ask which area or neighbourhood they prefer.
When user asks to refine by type ask if they want apartment, villa, house, plot or commercial.
When user asks to schedule a visit say: "Great! Please share your name and contact number and our agent will reach out to you within 24 hours."
Always remember previous conversation context and use it to give better recommendations."""


def search_web_for_properties(query):
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search"
            }],
            messages=[{
                "role": "user",
                "content": f"Search for real estate properties in India: {query}. Find maximum 3 listings from 99acres, MagicBricks or Housing.com. Return only property name, location, price and area. Be very brief."
            }]
        )

        web_results = ""
        for block in response.content:
            if hasattr(block, 'text'):
                web_results += block.text
        return web_results
    except Exception:
        return ""


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

    web_context = ""
    full_message = user_message + property_context + web_context

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
