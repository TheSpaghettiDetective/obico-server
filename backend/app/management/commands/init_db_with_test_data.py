import os
from binascii import hexlify
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.commands import flush

from app.models import User, Printer


class Command(BaseCommand):
    help = 'Drops all database content and loads test data.'
    user = None

    def create_printers(self, count=1):
        objects = [
            Printer(
                name=f"Printer {i}",
                user=self.user,
                auth_token=hexlify(os.urandom(10)).decode()
            ) for i in range(count)
        ]
        Printer.objects.bulk_create(objects)


    def handle(self, *args, **options):
        print("WARNING: This action removes ALL data from the current database and replace it with test data")
        response = input("Continue? [y/N] ")
        if response.lower() != "y":
            return
        # Flush database
        call_command(flush.Command())
        print("Creating superuser...")
        self.user = User.objects.create_superuser('test@test.com', 'test')
        print("Creating printers...")
        self.create_printers()
