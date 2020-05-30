from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import octoprint_views
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'printers', views.PrinterViewSet, 'Printer')
router.register(r'prints', views.PrintViewSet, 'Print')
router.register(r'gcodes', views.GCodeFileViewSet, 'GCodeFile')
router.register(
    r'printshotfeedback',
    views.PrintShotFeedbackViewSet,
    'PrintShotFeedback')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/octo/pic/', octoprint_views.OctoPrintPicView.as_view()),
    path('v1/octo/ping/', octoprint_views.OctoPrintPingView.as_view()),
]
