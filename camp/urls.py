from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet,PracticeViewSet,CampaignViewSet,MessageViewSet,AdminCampaignViewSet
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

router = DefaultRouter()
router.register(r'UserProfile', UserProfileViewSet, basename='UserProfile')
router.register(r'Practice', PracticeViewSet, basename='Practice')
router.register(r'Campaign', CampaignViewSet, basename='Campaign')
router.register(r'AdminCampaign', AdminCampaignViewSet, basename='AdminCampaign')
router.register(r'Message', MessageViewSet, basename='Message')

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('login/',login_view,name='login'),
    # path('logout/',logout_view,name='logout'),
]
