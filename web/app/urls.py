from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('printers/', views.PrinterView.as_view())
]
