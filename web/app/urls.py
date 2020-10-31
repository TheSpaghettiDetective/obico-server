from django.urls import path, re_path

from .views import web_views
from .views import tunnel_views
from .views import mobile_views
from .views import vue_demo

urlpatterns = [
    path('', web_views.index, name='index'),
    path('consent/', web_views.consent),
    path('media/<path:file_path>', web_views.serve_jpg_file),  # semi hacky solution to serve image files
    path('printer_auth_token/<int:pk>/', web_views.printer_auth_token, name='printer_auth_token'),
    path('printers/', web_views.printers),
    path('printers/<pk>/', web_views.edit_printer),
    path('printers/<int:pk>/delete/', web_views.delete_printer),
    path('printers/<int:pk>/share/', web_views.share_printer),
    path('printers/<int:pk>/control/', web_views.control_printer),
    path('printers/<int:pk>/integration/', web_views.integration),
    path('printers/share_token/<share_token>/', web_views.printer_shared, name='printer_shared'),
    path('publictimelapses/', web_views.publictimelapse_list, name='publictimelapse_list'),
    path('user_preferences/', web_views.user_preferences),
    path('test_telegram', web_views.test_telegram),
    path('unsubscribe_email/', web_views.unsubscribe_email),
    path('prints/<int:pk>/cancel/', web_views.cancel_print),
    path('prints/<int:pk>/resume/', web_views.resume_print),
    path('prints/', web_views.prints, name='prints'),
    path('prints/upload/', web_views.upload_print),
    path('prints/<pk>/', web_views.print),
    path('prints/shot-feedback/<pk>/', web_views.print_shot_feedback),
    path('gcodes/', web_views.gcodes),
    path('gcodes/upload/', web_views.upload_gcode_file,),
    path('secure_redirect/', web_views.secure_redirect, name='secure_redirect'),

    re_path(r'^octoprint/(?P<printer_id>\d+)',
        tunnel_views.octoprint_http_tunnel,
        name='octoprint_http_tunnel'),
    path('tunnel/<int:printer_id>/', tunnel_views.tunnel),

    # Shown only in mobile apps
    path('mobile/auth/login/', mobile_views.MobileLoginView.as_view(), name='mobile_auth_login'),
    path('mobile/auth/signup/', mobile_views.MobileSignupView.as_view(), name='mobile_auth_signup'),
    path('mobile/auth/fetch/', mobile_views.fetch_session),
    path('mobile/auth/oauth_callback/', mobile_views.oauth_callback),
    path('mobile/prints/', web_views.prints, {"template_dir": "mobile"}),

    # vue demo urls
    path('vue-demo/simple/', vue_demo.SimpleAppView.as_view(), name='vue-demo-simple'),
    path('vue-demo/multi/', vue_demo.MultiAppView.as_view(), name='vue-demo-multi'),
]
