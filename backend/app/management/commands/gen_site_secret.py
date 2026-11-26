import secrets
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generate a random site secret. Please note this only display the secret. You need to manually insert '

    def handle(self, *args, **options):
        print(f'''
DJANGO_SECRET_KEY={secrets.token_urlsafe()}

Please:

1. Copy the line above into ".env" file in the "obico-server" folder;
2. Restart the Obico Server. It re-signs the links to your media files when it starts.

For more info, please check https://obico.io/docs/server-guides/configure/#re-generate-django_secret_key
''')