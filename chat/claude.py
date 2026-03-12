import ollama

SYSTEM_PROMPT = """You are a helpful real estate assistant. You help users with queries about buying, selling, and renting properties.

You ONLY answer questions related to:
- Property buying, selling and renting
- Property prices and market trends
- Property locations and neighbourhoods
- Home loans and financing
- Legal aspects of property deals
- Property types like apartments, villas, plots and commercial spaces

If the user asks anything outside of real estate, politely say:
"I can only help with real estate related queries. Please ask me anything about properties, buying, selling or renting."

Always be helpful, friendly and professional. When you have property listings available, mention them naturally in your response."""


def get_ai_response(user_message, conversation_history, relevant_properties=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    if relevant_properties:
        property_context = "\n\nRelevant properties from our listings:\n"
        for prop in relevant_properties:
            property_context += f"""
- {prop.title}
  Type: {prop.property_type}
  Location: {prop.location}, {prop.city}
  Price: Rs.{prop.price}
  Area: {prop.area_sqft} sqft
  Bedrooms: {prop.bedrooms}
  Description: {prop.description}
"""
        user_message = user_message + property_context

    messages.append({"role": "user", "content": user_message})

    stream = ollama.chat(
        model="llama3.2",
        messages=messages,
        stream=True
    )

    for chunk in stream:
        yield chunk["message"]["content"]


def get_ai_response_full(user_message, conversation_history, relevant_properties=None):
    full_response = ""
    for chunk in get_ai_response(user_message, conversation_history, relevant_properties):
        full_response += chunk
    return full_response