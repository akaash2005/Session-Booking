from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
import requests as http_requests
from .serializers import UserSerializer, UpdateProfileSerializer

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class GoogleAuthView(APIView):
    permission_classes = []

    def post(self, request):
        token = request.data.get('access_token')
        if not token:
            return Response({'error': 'Access token required'}, status=400)

        google_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        res = http_requests.get(google_url, headers={'Authorization': f'Bearer {token}'})
        if res.status_code != 200:
            return Response({'error': 'Invalid Google token'}, status=400)

        data = res.json()
        email = data.get('email')
        if not email:
            return Response({'error': 'Email not found'}, status=400)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': data.get('given_name', ''),
                'last_name': data.get('family_name', ''),
                'avatar': data.get('picture', ''),
            }
        )

        tokens = get_tokens_for_user(user)
        return Response({**tokens, 'user': UserSerializer(user).data})


class GitHubAuthView(APIView):
    permission_classes = []

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code required'}, status=400)

        import os
        token_res = http_requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': os.environ.get('GITHUB_CLIENT_ID'),
                'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
                'code': code,
            },
            headers={'Accept': 'application/json'}
        )
        token_data = token_res.json()
        access_token = token_data.get('access_token')
        if not access_token:
            return Response({'error': 'Failed to get access token'}, status=400)

        user_res = http_requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_data = user_res.json()

        email_res = http_requests.get(
            'https://api.github.com/user/emails',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        emails = email_res.json()
        primary_email = next(
            (e['email'] for e in emails if e.get('primary') and e.get('verified')),
            None
        )
        if not primary_email:
            return Response({'error': 'No verified email found'}, status=400)

        user, created = User.objects.get_or_create(
            email=primary_email,
            defaults={
                'username': user_data.get('login', primary_email.split('@')[0]),
                'first_name': (user_data.get('name') or '').split(' ')[0],
                'last_name': ' '.join((user_data.get('name') or '').split(' ')[1:]),
                'avatar': user_data.get('avatar_url', ''),
            }
        )

        tokens = get_tokens_for_user(user)
        return Response({**tokens, 'user': UserSerializer(user).data})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=400)


class BecomeCreatorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Promote authenticated user to creator role"""
        user = request.user
        if user.role == User.Role.CREATOR:
            return Response({'message': 'You are already a creator!'}, status=200)
        
        user.role = User.Role.CREATOR
        user.save()
        return Response({
            'message': 'You are now a creator!',
            'user': UserSerializer(user).data
        })


class BecomeUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Demote creator back to regular user"""
        user = request.user
        if user.role == User.Role.USER:
            return Response({'message': 'You are already a user!'}, status=200)
        
        user.role = User.Role.USER
        user.save()
        return Response({
            'message': 'You are now a regular user!',
            'user': UserSerializer(user).data
        })