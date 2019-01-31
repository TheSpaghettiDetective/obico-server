from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('printers/', views.printers, name='printers'),
    path('printers/new/', views.new_printer, name='new_printer'),
    path('printers/<int:id>/', views.edit_printer, name='edit_printer'),
    path('printers/<int:id>/delete/', views.delete_printer, name='delete_printer'),
    path('timelapse_gallery/', views.timelapse_gallery, name='timelapse_gallery'),
]
