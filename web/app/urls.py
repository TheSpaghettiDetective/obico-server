from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('media/<path:file_path>', views.serve_jpg_file, name='serve_jpg_file'), # semi hacky solution to serve image files
    path('printers/', views.printers, name='printers'),
    path('printers/new/', views.new_printer, name='printers_new'),
    path('printers/<int:pk>/', views.edit_printer, name='printers_edit'),
    path('printers/<int:pk>/delete/', views.delete_printer, name='printers_delete'),
    path('printers/<int:pk>/cancel/', views.cancel_printer, name='printers_cancel'),
    path('printers/<int:pk>/resume/', views.resume_printer, name='printers_resume'),
    path('publictimelapses/', views.publictimelapse_list, name='publictimelapse_list'),
    path('user_preferences/', views.user_preferences, name='user_preferences'),
    path('phone_verification/', views.phone_verification, name='phone_verification'),
    path('phone_token_validation/', views.phone_token_validation, name='phone_token_validation'),
    path('prints/', views.prints, name='prints'),
]
