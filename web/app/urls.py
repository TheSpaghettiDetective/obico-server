from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('consent/', views.consent, name='consent'),
    path('media/<path:file_path>', views.serve_jpg_file, name='serve_jpg_file'), # semi hacky solution to serve image files
    path('printer_auth_token/<int:pk>/', views.priner_auth_token, name='priner_auth_token'),
    path('printers/', views.printers, name='printers'),
    path('printers/<pk>/', views.edit_printer, name='edit_printer'),
    path('printers_turn/', views.printers_turn, name='printers_turn'),
    path('printers/<int:pk>/delete/', views.delete_printer, name='delete_printer'),
    path('printers/<int:pk>/cancel/', views.cancel_printer, name='cancel_printer'),
    path('printers/<int:pk>/resume/', views.resume_printer, name='resume_printer'),
    path('printers/<int:pk>/share/', views.share_printer, name='share_printer'),
    path('printers/shared/<share_token>/', views.printer_shared, name='printer_shared'),
    path('publictimelapses/', views.publictimelapse_list, name='publictimelapse_list'),
    path('user_preferences/', views.user_preferences, name='user_preferences'),
    path('prints/', views.prints, name='prints'),
    path('prints/upload/', views.upload_print, name='upload_print'),
    path('prints/delete/<pk>/', views.delete_prints, name='prints_delete'),
    path('webrtc/', views.webrtc, name='webrtc'),
]
