from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import FileResponse
from .models import Session
from .serializers import SessionSerializer, SessionWriteSerializer
from .permissions import IsCreatorOrReadOnly

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.filter(status='published')
    permission_classes = [IsCreatorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['date', 'price', 'created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SessionWriteSerializer
        return SessionSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_creator:
            # Creators see their own sessions (unpublished too)
            return Session.objects.filter(creator=self.request.user)
        # Everyone else sees published sessions
        return Session.objects.filter(status='published')

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def upload_image(self, request, pk=None):
        """Upload cover image for session"""
        session = self.get_object()
        
        if request.user != session.creator:
            return Response(
                {'error': 'You can only upload images for your own sessions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validate file size (max 5MB)
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Image file too large. Maximum size is 5MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid image format. Allowed: JPEG, PNG, GIF, WebP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.cover_image = image_file
        session.save()
        
        return Response({
            'message': 'Image uploaded successfully',
            'url': f'/api/sessions/{session.id}/image/'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def image(self, request, pk=None):
        """Serve session cover image through backend proxy"""
        session = self.get_object()
        
        if not session.cover_image:
            return Response(
                {'error': 'No image for this session'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            file_obj = session.cover_image.open('rb')
            
            # Detect content type from filename
            filename = session.cover_image.name.lower()
            if filename.endswith('.png'):
                content_type = 'image/png'
            elif filename.endswith('.gif'):
                content_type = 'image/gif'
            elif filename.endswith('.webp'):
                content_type = 'image/webp'
            else:
                content_type = 'image/jpeg'
            
            response = FileResponse(file_obj, content_type=content_type)
            response['Content-Disposition'] = 'inline'
            response['Cache-Control'] = 'max-age=86400'
            return response
        except Exception as e:
            print(f"Error serving image: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error serving image: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


