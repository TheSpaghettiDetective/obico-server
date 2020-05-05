from django.urls import path

from .views import index, prints

urlpatterns = [
    path('', index, name='index'),
    path('prints/', prints, name="prints")
    # path('delete/<int:pk>', TodoDetailView.as_view()),
]