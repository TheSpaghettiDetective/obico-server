"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from functools import wraps

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.urls import path, include
from django.conf import settings
from oauth2_provider import urls as oauth2_urls, views as oauth2_views


def staff_only(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped


# Only staff register and manage OAuth applications: the consent page shows the
# name the registrant chose, so an application must be one we set up. Everyone
# keeps the authorization flow and the page listing the apps they authorized.
oauth2_application_urlpatterns = [
    path('applications/', staff_only(oauth2_views.ApplicationList.as_view()), name='list'),
    path('applications/register/', staff_only(oauth2_views.ApplicationRegistration.as_view()), name='register'),
    path('applications/<slug:pk>/', staff_only(oauth2_views.ApplicationDetail.as_view()), name='detail'),
    path('applications/<slug:pk>/delete/', staff_only(oauth2_views.ApplicationDelete.as_view()), name='delete'),
    path('applications/<slug:pk>/update/', staff_only(oauth2_views.ApplicationUpdate.as_view()), name='update'),
]
oauth2_urlpatterns = oauth2_application_urlpatterns + [
    p for p in oauth2_urls.urlpatterns
    if p.name not in {p.name for p in oauth2_application_urlpatterns}
]

urlpatterns = [
    path('', include('app.urls')),
    path('accounts/', include('allauth.urls')),
    path('o/', include((oauth2_urlpatterns, 'oauth2_provider'), namespace='oauth2_provider')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]
