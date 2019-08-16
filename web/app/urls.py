from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('media/<path:file_path>', views.serve_jpg_file, name='serve_jpg_file'), # semi hacky solution to serve image files
    path('printer_auth_token/<int:pk>/', views.priner_auth_token, name='priner_auth_token'),
    path('printers/', views.printers, name='printers'),
    path('printers/<pk>/', views.edit_printer, name='printers_edit'),
    path('printers/<int:pk>/delete/', views.delete_printer, name='printers_delete'),
    path('printers/<int:pk>/cancel/', views.cancel_printer, name='printers_cancel'),
    path('printers/<int:pk>/resume/', views.resume_printer, name='printers_resume'),
    path('publictimelapses/', views.publictimelapse_list, name='publictimelapse_list'),
    path('user_preferences/', views.user_preferences, name='user_preferences'),
    path('prints/', views.prints, name='prints'),
    path('prints/delete/<pk>/', views.delete_prints, name='prints_delete'),
    path('user_credits/', views.user_credits, name='user_credits'),
    path('telegram/', views.telegram, name='telegram'),
]
