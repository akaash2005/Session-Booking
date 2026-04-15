from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GoogleAuthView, GitHubAuthView, ProfileView, BecomeCreatorView, BecomeUserView

urlpatterns = [
    path('google/', GoogleAuthView.as_view(), name='google-auth'),
    path('github/', GitHubAuthView.as_view(), name='github-auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('become-creator/', BecomeCreatorView.as_view(), name='become-creator'),
    path('become-user/', BecomeUserView.as_view(), name='become-user'),
]