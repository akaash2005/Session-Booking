import razorpay
import hashlib
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.bookings.models import Booking
from .models import Payment
from .serializers import PaymentSerializer


# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET'))
)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a Razorpay order for a booking"""
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response({'error': 'booking_id is required'}, status=400)
        
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=404)
        
        # Check if payment already exists and is not failed/cancelled
        if hasattr(booking, 'payment'):
            existing_payment = booking.payment
            if existing_payment.status not in [Payment.Status.FAILED, Payment.Status.CANCELLED]:
                return Response({
                    'razorpay_order_id': existing_payment.razorpay_order_id,
                    'payment_id': existing_payment.id,
                    'amount': booking.session.price
                }, status=200)
        
        amount_paise = int(booking.session.price * 100)  # Razorpay uses paise
        
        try:
            # Create Razorpay Order
            order_data = {
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f'booking_{booking_id}',
                'notes': {
                    'booking_id': str(booking_id),
                    'session_id': str(booking.session.id),
                    'user_id': str(request.user.id)
                }
            }
            
            order = razorpay_client.order.create(data=order_data)
            
            # Save payment record
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'razorpay_order_id': order['id'],
                    'amount': booking.session.price,
                    'currency': 'INR',
                    'status': Payment.Status.PENDING
                }
            )
            
            return Response({
                'razorpay_order_id': order['id'],
                'payment_id': payment.id,
                'amount': booking.session.price,
                'currency': 'INR',
                'razorpay_key_id': os.environ.get('RAZORPAY_KEY_ID'),
                'user_email': request.user.email,
                'user_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
            }, status=201)
        
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verify payment signature and confirm booking"""
        payment_id = request.data.get('payment_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        razorpay_order_id = request.data.get('razorpay_order_id')
        
        if not all([payment_id, razorpay_payment_id, razorpay_signature, razorpay_order_id]):
            return Response({'error': 'Missing payment details'}, status=400)
        
        try:
            payment = Payment.objects.get(id=payment_id, booking__user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)
        
        try:
            # Verify signature
            generated_signature = hashlib.sha256(
                f'{razorpay_order_id}|{razorpay_payment_id}'.encode()
            ).hexdigest()
            
            if generated_signature != razorpay_signature:
                payment.status = Payment.Status.FAILED
                payment.save()
                return Response({'error': 'Payment verification failed'}, status=400)
            
            # Update payment with Razorpay IDs
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = Payment.Status.SUCCESS
            payment.save()
            
            # Update booking status
            payment.booking.status = 'confirmed'
            payment.booking.save()
            
            return Response({
                'message': 'Payment verified successfully',
                'payment': PaymentSerializer(payment).data
            }, status=200)
        
        except Exception as e:
            return Response({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    """Handle Razorpay webhooks"""
    
    def post(self, request):
        """Process webhook from Razorpay"""
        try:
            event = request.data
            event_type = event.get('event')
            
            # payment.authorized
            if event_type == 'payment.authorized':
                payload = event.get('payload', {}).get('payment', {}).get('entity', {})
                razorpay_payment_id = payload.get('id')
                order_id = payload.get('order_id')
                
                payment = Payment.objects.filter(razorpay_order_id=order_id).first()
                if payment:
                    payment.razorpay_payment_id = razorpay_payment_id
                    payment.status = Payment.Status.AUTHORIZED
                    payment.save()
            
            # payment.failed
            elif event_type == 'payment.failed':
                payload = event.get('payload', {}).get('payment', {}).get('entity', {})
                order_id = payload.get('order_id')
                
                payment = Payment.objects.filter(razorpay_order_id=order_id).first()
                if payment:
                    payment.status = Payment.Status.FAILED
                    payment.save()
            
            # payment.captured
            elif event_type == 'payment.captured':
                payload = event.get('payload', {}).get('payment', {}).get('entity', {})
                razorpay_payment_id = payload.get('id')
                order_id = payload.get('order_id')
                
                payment = Payment.objects.filter(razorpay_order_id=order_id).first()
                if payment:
                    payment.razorpay_payment_id = razorpay_payment_id
                    payment.status = Payment.Status.SUCCESS
                    payment.save()
                    
                    # Update booking
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
            
            return Response({'status': 'success'}, status=200)
        
        except Exception as e:
            return Response({'error': str(e)}, status=400)

