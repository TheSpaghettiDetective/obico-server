from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20210119_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pushover_user_token',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='print_notification_by_pushover',
            field=models.BooleanField(default=True),
        )
    ]
