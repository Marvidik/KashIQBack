# users/views.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.hashers import make_password
from django.db import transaction

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password'}, status=403)

    if not user.check_password(password):
        return Response({'error': 'Invalid email or password'}, status=403)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        
        'id':user.id,
        'token': token.key,
        'username': user.username,
        'email': user.email,
    })



@api_view(['POST'])
@authentication_classes([])  
@permission_classes([AllowAny])  # allow public registration
def register(request):
    try:
        data = request.data

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        

        # Core user creation in atomic block
        with transaction.atomic():
            # Create user
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )
            
            
            # Generate token
            token, _ = Token.objects.get_or_create(user=user)
      

        return Response({
            'message': 'User registered successfully',
            'token': token.key,
            'user': {
                'id':user.id,
                'username': username,
                'email': email
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)