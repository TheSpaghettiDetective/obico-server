from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import octoprint_views
from . import viewsets
from . import public_viewsets

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', viewsets.UserViewSet, 'User')
router.register(r'printers', viewsets.PrinterViewSet, 'Printer')
router.register(r'prints', viewsets.PrintViewSet, 'Print')
router.register(r'gcodes', viewsets.GCodeFileViewSet, 'GCodeFile')
router.register(
    r'printshotfeedbacks',
    viewsets.PrintShotFeedbackViewSet,
    'PrintShotFeedback')
router.register(
    r'tunnelusage',
    viewsets.OctoPrintTunnelUsageViewSet,
    'OctoPrintTunnelUsage')
router.register(r'mobile_devices', viewsets.MobileDeviceViewSet, 'MobileDevice')
router.register(
    r'onetimeverificationcodes',
    viewsets.OneTimeVerificationCodeViewSet,
    'OneTimeVerificationCodeViewSet')

pub_router = DefaultRouter()
pub_router.register(r'printer', public_viewsets.PrinterViewSet, 'Printer')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1p/', include(pub_router.urls)),
    path('v1/octo/pic/', octoprint_views.OctoPrintPicView.as_view()),
    path('v1/octo/ping/', octoprint_views.OctoPrintPingView.as_view()),
]
