from django.urls import path

from . import views
from . import vue_demo

urlpatterns = [
    path('', views.index, name='index'),
    path('consent/', views.consent, name='consent'),
    path('media/<path:file_path>', views.serve_jpg_file, name='serve_jpg_file'),  # semi hacky solution to serve image files
    path('printer_auth_token/<int:pk>/', views.printer_auth_token, name='printer_auth_token'),
    path('printers/', views.printers, name='printers'),
    path('printers/<pk>/', views.edit_printer, name='edit_printer'),
    path('printers/<int:pk>/delete/', views.delete_printer, name='delete_printer'),
    path('printers/<int:pk>/share/', views.share_printer, name='share_printer'),
    path('printers/<int:pk>/control/', views.control_printer, name='control_printer'),
    path('printers/<int:pk>/integration/', views.integration, name='integration'),
    path('printers/shared/<share_token>/', views.printer_shared, name='printer_shared'),
    path('publictimelapses/', views.publictimelapse_list, name='publictimelapse_list'),
    path('user_preferences/', views.user_preferences, name='user_preferences'),
    path('test_telegram', views.test_telegram, name='test_telegram'),
    path('unsubscribe_email/', views.unsubscribe_email, name='unsubscribe_email'),
    path('prints/<int:pk>/cancel/', views.cancel_print, name='cancel_print'),
    path('prints/<int:pk>/resume/', views.resume_print, name='resume_print'),
    path('prints/', views.prints, name='prints'),
    path('prints/upload/', views.upload_print, name='upload_print'),
    path('prints/<pk>/', views.print, name='print'),
    path('prints/delete/<pk>/', views.delete_prints, name='prints_delete'),
    path('prints/shot-feedback/<pk>/', views.print_shot_feedback, name='print_shot_feedback'),
    path('gcodes/', views.gcodes, name='gcodes'),
    path('gcodes/upload/', views.upload_gcode_file, name='upload_gcode_file'),
    path('secure_redirect/', views.secure_redirect, name='secure_redirect'),

    # vue demo urls
    path('vue-demo/simple/', vue_demo.SimpleAppView.as_view(), name='vue-demo-simple'),
    path('vue-demo/multi/', vue_demo.MultiAppView.as_view(), name='vue-demo-multi'),
]
