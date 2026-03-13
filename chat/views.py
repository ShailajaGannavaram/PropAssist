import uuid
import json
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from .claude import get_ai_response, get_ai_response_full
from properties.models import Property
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .lead_detector import detect_and_save_lead


def search_properties(user_message, conversation_history=None):
    message_lower = user_message.lower()

    cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'pune', 'kolkata']
    found_city = next((city for city in cities if city in message_lower), None)

    if not found_city and conversation_history:
        for msg in reversed(list(conversation_history)):
            for city in cities:
                if city in msg.content.lower():
                    found_city = city
                    break
            if found_city:
                break

    area_to_city = {
        'madhapur': 'hyderabad', 'gachibowli': 'hyderabad',
        'kondapur': 'hyderabad', 'banjara hills': 'hyderabad',
        'jubilee hills': 'hyderabad', 'hitec city': 'hyderabad',
        'kukatpally': 'hyderabad', 'attapur': 'hyderabad',
        'whitefield': 'bangalore', 'koramangala': 'bangalore',
        'indiranagar': 'bangalore', 'hsr layout': 'bangalore',
        'electronic city': 'bangalore', 'jp nagar': 'bangalore',
        'bandra': 'mumbai', 'andheri': 'mumbai', 'powai': 'mumbai',
        'hinjewadi': 'pune', 'kothrud': 'pune', 'wakad': 'pune',
        'anna nagar': 'chennai', 'velachery': 'chennai', 'adyar': 'chennai',
        'salt lake': 'kolkata', 'new town': 'kolkata',
        'dwarka': 'delhi', 'noida': 'delhi', 'gurgaon': 'delhi',
    }

    if not found_city:
        for area, city in area_to_city.items():
            if area in message_lower:
                found_city = city
                break

    property_types = ['apartment', 'flat', 'house', 'villa', 'plot', 'commercial', 'office']
    found_type = next((pt for pt in property_types if pt in message_lower), None)
    if not found_type and conversation_history:
        for msg in reversed(list(conversation_history)):
            found_type = next((pt for pt in property_types if pt in msg.content.lower()), None)
            if found_type:
                break
    if found_type == 'flat':
        found_type = 'apartment'

    filters = Q(is_available=True)
    if found_city:
        filters &= (Q(city__icontains=found_city) | Q(location__icontains=found_city))
    if found_type:
        filters &= Q(property_type__icontains=found_type)

    properties = Property.objects.filter(filters).order_by('?')[:5]

    if not properties.exists() and found_city:
        properties = Property.objects.filter(
            Q(city__icontains=found_city) | Q(location__icontains=found_city),
            is_available=True
        ).order_by('?')[:5]

    return properties


@csrf_exempt
def chat_stream(request):
    if request.method != "POST":
        return Response({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", str(uuid.uuid4()))

    if not user_message:
        return Response({"error": "Message required"}, status=400)

    conversation, created = Conversation.objects.get_or_create(session_id=session_id)
    history = conversation.messages.all().order_by("created_at")
    relevant_properties = search_properties(user_message, history)

    Message.objects.create(conversation=conversation, role="user", content=user_message)
    detect_and_save_lead(user_message, session_id, history)

    full_reply = []

    def stream_generator():
        for chunk in get_ai_response(user_message, history, relevant_properties):
            full_reply.append(chunk)
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        complete_reply = "".join(full_reply)
        Message.objects.create(conversation=conversation, role="assistant", content=complete_reply)
        yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

    response = StreamingHttpResponse(stream_generator(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@api_view(['POST'])
def chat(request):
    user_message = request.data.get('message', '').strip()
    session_id = request.data.get('session_id', str(uuid.uuid4()))

    if not user_message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    conversation, created = Conversation.objects.get_or_create(session_id=session_id)
    history = conversation.messages.all().order_by('created_at')
    relevant_properties = search_properties(user_message, history)

    Message.objects.create(conversation=conversation, role='user', content=user_message)
    detect_and_save_lead(user_message, session_id, history)

    ai_reply = get_ai_response_full(user_message, history, relevant_properties)
    Message.objects.create(conversation=conversation, role='assistant', content=ai_reply)

    return Response({'reply': ai_reply, 'session_id': session_id})


@api_view(['GET'])
def get_history(request, session_id):
    try:
        conversation = Conversation.objects.get(session_id=session_id)
        messages = conversation.messages.all().order_by('created_at')
        history = [{'role': msg.role, 'content': msg.content} for msg in messages]
        return Response({'history': history})
    except Conversation.DoesNotExist:
        return Response({'history': []})
