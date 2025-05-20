from django.db import models

from app.models import User
from app_ent.models import GCodeFile

class JusPrinChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    messages = models.TextField(null=False, blank=False)
    machine_name = models.TextField(null=True, blank=True)
    filament_name = models.TextField(null=True, blank=True)
    print_process_name = models.TextField(null=True, blank=True)
    slicing_settings_json = models.TextField(null=True, blank=True)
    g_code_file = models.ForeignKey(GCodeFile, on_delete=models.SET_NULL, null=True, blank=True)
    user_feedback = models.CharField(max_length=16, null=True, blank=True)
    user_feedback_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
