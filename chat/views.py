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
from django.utils.decorators import method_decorator


def search_properties(user_message):
    cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'pune', 'kolkata', 'kondapur']
    found_city = next((city for city in cities if city in user_message.lower()), None)

    property_types = ['apartment', 'house', 'villa', 'plot', 'commercial']
    found_type = next((pt for pt in property_types if pt in user_message.lower()), None)

    filters = Q(is_available=True)
    if found_city:
        filters &= Q(city__icontains=found_city)
    if found_type:
        filters &= Q(property_type__icontains=found_type)

    properties = Property.objects.filter(filters)[:5]
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
    relevant_properties = search_properties(user_message)

    Message.objects.create(conversation=conversation, role="user", content=user_message)

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
    relevant_properties = search_properties(user_message)

    Message.objects.create(conversation=conversation, role='user', content=user_message)

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