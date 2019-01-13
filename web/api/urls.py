from django.urls import path
from . import views

urlpatterns = [
    path('printer/status', views.PrinterStatusView.as_view()),
    path('printer/pic', views.PrinterPicView.as_view()),
]