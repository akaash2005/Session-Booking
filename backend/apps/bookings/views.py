from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer
from .throttles import BookingThrottle
class BookingViewSet(viewsets.ModelViewSet):
    
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    throttle_classes = [BookingThrottle]
    def get_queryset(self):
        user = self.request.user
        if user.is_creator:
            # Creators see bookings for their sessions
            return Booking.objects.filter(session__creator=user)
        return Booking.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def my(self, request):
        """Get current user's bookings"""
        bookings = self.get_queryset()
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.user != request.user:
            return Response({'error': 'Not allowed'}, status=403)
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response(BookingSerializer(booking).data)