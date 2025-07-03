from django.db import models

from app.models import User

class JusPrinChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    messages = models.TextField(null=False, blank=False)
    machine_name = models.TextField(null=True, blank=True)
    filament_name = models.TextField(null=True, blank=True)
    print_process_name = models.TextField(null=True, blank=True)
    slicing_settings_json = models.TextField(null=True, blank=True)
    user_feedback = models.CharField(max_length=16, null=True, blank=True)
    user_feedback_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JusPrinAICredit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    ai_credit_free_monthly_quota = models.IntegerField(null=False, default=-1)
    ai_credit_used_current_month = models.IntegerField(null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.ai_credit_used_current_month}/{self.ai_credit_free_monthly_quota}"



