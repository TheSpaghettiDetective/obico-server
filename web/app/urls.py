from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('printers/', login_required(views.PrinterList.as_view())),
    path('printers/new/', views.new_printer, name='printers_new'),
    path('printers/<int:id>/', views.edit_printer, name='printers_edit'),
    path('printers/<int:id>/delete/', views.delete_printer, name='printers_delete'),
    path('printers/<int:id>/cancel/', views.delete_printer, name='printers_cancel'),
    path('printers/<int:id>/resume/', views.delete_printer, name='printers_resume'),
    path('publictimelapses/', views.publictimelapse_list, name='publictimelapse_list'),
]
