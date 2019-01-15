from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import dev_views
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'printers', views.PrinterViewSet, 'Printer')

urlpatterns = [
    path('', include(router.urls)),
    path('printer/status', dev_views.PrinterStatusView.as_view()),
    path('printer/pic', dev_views.PrinterPicView.as_view()),
]