from rest_framework import serializers
from .models import Session
from apps.accounts.serializers import UserSerializer

class SessionSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    spots_left = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'creator', 'title', 'description', 'price',
            'date', 'duration_minutes', 'max_participants',
            'status', 'cover_image', 'tags',
            'spots_left', 'is_available', 'created_at'
        ]
        read_only_fields = ['id', 'creator', 'created_at']

    def get_cover_image(self, obj):
        """Return image endpoint path (without /api prefix)"""
        if obj.cover_image:
            return f'sessions/{obj.id}/image/'
        return None

class SessionWriteSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'description', 'price', 'date',
            'duration_minutes', 'max_participants',
            'status', 'cover_image', 'tags'
        ]
        read_only_fields = ['id', 'cover_image']

    def get_cover_image(self, obj):
        """Return image endpoint path (without /api prefix)"""
        if obj.cover_image:
            return f'sessions/{obj.id}/image/'
        return None