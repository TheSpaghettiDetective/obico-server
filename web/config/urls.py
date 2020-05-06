from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('app.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls)
]
