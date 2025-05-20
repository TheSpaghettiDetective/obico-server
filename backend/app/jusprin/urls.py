from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views as jusprin_views

router = DefaultRouter()

router.register(r'chats', jusprin_views.JusPrinChatViewSet, 'JusPrinChatViewSet')
router.register(r'plate_analysis', jusprin_views.JusPrinPlateAnalysisViewSet, 'JusPrinPlateAnalysisViewSet')
router.register(r'contact_support', jusprin_views.JusPrinContactSupportRequestViewSet, 'JusPrinContactSupportRequestViewSet')


urlpatterns = [
    path('v0.3/embedded_chat/', jusprin_views.embedded_chat_v03, name='embedded_chat_v03'),
    path('v0.4/embedded_chat/', jusprin_views.embedded_chat_v04, name='embedded_chat_v04'),
    path('v1.0/embedded_chat/', jusprin_views.embedded_chat_v10, name='embedded_chat_v10'),
    path('api/', include(router.urls)),
]
