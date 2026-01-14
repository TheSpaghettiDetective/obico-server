from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic.base import RedirectView

from . import views as jusprin_views

router = DefaultRouter()

router.register(r'me', jusprin_views.JusPrinMeViewSet, 'JusPrinMeViewSet')
router.register(r'chats', jusprin_views.JusPrinChatViewSet, 'JusPrinChatViewSet')
router.register(r'plate_analysis', jusprin_views.JusPrinPlateAnalysisViewSet, 'JusPrinPlateAnalysisViewSet')
router.register(r'contact_support', jusprin_views.JusPrinContactSupportRequestViewSet, 'JusPrinContactSupportRequestViewSet')


urlpatterns = [
    path('v0.4/embedded_chat/', RedirectView.as_view(url='/jusprin/v1.0/embedded_chat/', permanent=True)),
    path('v1.0/embedded_chat/', jusprin_views.embedded_chat_v10, name='embedded_chat_v10'),
    path('v1.2/embedded_chat/', jusprin_views.embedded_chat_v12, name='embedded_chat_v12'),
    path('api/', include(router.urls)),
]
