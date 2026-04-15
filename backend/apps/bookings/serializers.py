from rest_framework import serializers
from django.db import IntegrityError
from .models import Booking
from apps.sessions_app.serializers import SessionSerializer

class BookingSerializer(serializers.ModelSerializer):
    session = SessionSerializer(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.sessions_app.models', fromlist=['Session']).Session.objects.all(),
        source='session',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = ['id', 'session', 'session_id', 'status', 'booked_at', 'notes']
        read_only_fields = ['id', 'booked_at', 'status']

    def validate(self, attrs):
        """Validate booking data before creation"""
        # Only validate on creation (POST), not updates
        if self.instance is not None:
            return attrs
        
        # Only validate if session is being set (write operations)
        if 'session' not in attrs:
            return attrs
            
        session = attrs['session']
        request = self.context.get('request')
        
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError('User not found in request')
        
        user = request.user
        
        # Check if already booked (excluding cancelled bookings)
        existing = Booking.objects.filter(
            user=user, 
            session=session,
            status__in=['confirmed', 'completed']  # Only check active bookings
        ).exists()
        
        if existing:
            raise serializers.ValidationError('You have already booked this session.')
        
        # Check if session is available
        if hasattr(session, 'is_available') and not session.is_available:
            raise serializers.ValidationError('This session is fully booked or unavailable.')
        
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError('You have already booked this session.')
