from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from chat.models import Message
from chat.serializers import MessageSerializer, UserSerializer

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return redirect('chats')
    return render(request, 'chat/index.html')

def chat_view(request):
    users = User.objects.exclude(username=request.user.username)
    # {'users': User.objects.exclude(username=request.user.username)}
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        
        return render(request, 'chat/chat.html', {'users': users})

def message_view(request, sender, receiver): 
    """Render the template with required context variables"""
    users = User.objects.exclude(username=request.user.username)
    receiver = User.objects.get(id=receiver)
    # Return context with message objects where users are either sender or receiver.
    messages = Message.objects.filter(sender_id=sender, receiver_id=receiver) | \
               Message.objects.filter(sender_id=receiver, receiver_id=sender)

    context = {'users': users, 'receiver': receiver,
               'messages': messages}
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        return render(request, "chat/messages.html", context)

@csrf_exempt
def user_list(request, pk=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        if pk:
            users = User.objects.filter(id=pk)
        else:
            users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': request}) 
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def message_list(request, sender=None, receiver=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        messages = Message.objects.filter(sender_id=sender, receiver_id=receiver, is_read=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
        