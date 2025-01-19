from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import octoprint_views
from . import viewsets

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', viewsets.UserViewSet, 'User')
router.register(r'printers', viewsets.PrinterViewSet, 'Printer')
router.register(r'prints', viewsets.PrintViewSet, 'Print')
router.register(r'g_code_files', viewsets.GCodeFileViewSet, 'GCodeFile')
router.register(r'g_code_folders', viewsets.GCodeFolderViewSet, 'GCodeFolder')
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
    'OneTimeVerificationCode')
router.register(
    r'sharedresources',
    viewsets.SharedResourceViewSet,
    'SharedResource')
router.register(
    r'printer_discovery',
    viewsets.PrinterDiscoveryViewSet,
    'PrinterDiscovery')
router.register(
    r'one_time_passcodes',
    viewsets.OneTimePasscodeViewSet,
    'OneTimePasscode')
router.register(r'tunnels', viewsets.OctoPrintTunnelViewSet, 'OctoPrintTunnel')
router.register(r'notification_settings', viewsets.NotificationSettingsViewSet, 'NotificationSettings')
router.register(r'printer_events', viewsets.PrinterEventViewSet, 'PrinterEvent')
router.register(r'first_layer_inspection_images', viewsets.FirstLayerInspectionImageViewSet, 'FirstLayerInspectionImage')
router.register(r'octo/g_code_files', octoprint_views.GCodeFileView, 'AgentGCodeFile')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/octo/pic/', octoprint_views.OctoPrintPicView.as_view()),
    path('v1/octo/ping/', octoprint_views.OctoPrinterView.as_view()),  # For compatibility with plugin < 1.5.0
    path('v1/octo/printer/', octoprint_views.OctoPrinterView.as_view()),
    path('v1/octo/unlinked/', octoprint_views.OctoPrinterDiscoveryView.as_view()),
    path('v1/octo/verify/',
         octoprint_views.OneTimeVerificationCodeVerifyView.as_view(),
    ),
    path('v1/octo/printer_events/', octoprint_views.PrinterEventView.as_view()),

    path('v1/version/', viewsets.ApiVersionView.as_view()),
]
