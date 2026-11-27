"""Deleting a user also deletes their JusPrin 1 rows, in any process.

Django deletes a user's rows only in the tables of models it has imported. A
process that never loads the URL conf, such as `manage.py shell` or a
management command, imports only each app's models module, so these models
must be imported from there.
"""
import os
import subprocess
import sys

from django.conf import settings
from django.test import TestCase

from app.jusprin.models import JusPrinAICredit, JusPrinChat
from app.models import User

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Run in a new process: in this one, the import above has already registered
# the models.
LIST_TABLES_A_USER_DELETE_REACHES = '''
import django
django.setup()
from django.db.models.deletion import get_candidate_relations_to_delete
from app.models import User
print(' '.join(sorted(r.related_model._meta.label for r in get_candidate_relations_to_delete(User._meta))))
'''


class UserDeleteReachesJusPrin1RowsTest(TestCase):
    def test_a_new_process_knows_the_jusprin_1_models_without_the_url_conf(self):
        result = subprocess.run(
            [sys.executable, '-c', LIST_TABLES_A_USER_DELETE_REACHES],
            cwd=BACKEND_DIR, capture_output=True, text=True,
            env={**os.environ, 'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', settings.SETTINGS_MODULE)})
        self.assertEqual(result.returncode, 0, result.stderr)
        labels = result.stdout.split()
        self.assertIn('app.JusPrinAICredit', labels)
        self.assertIn('app.JusPrinChat', labels)

    def test_deleting_a_user_deletes_their_credit_row_and_chats(self):
        user = User.objects.create(email='jusprin1-rows@example.com')
        JusPrinAICredit.objects.get_or_create(user=user)
        JusPrinChat.objects.create(user=user, messages='[]')

        user.delete()

        self.assertFalse(User.objects.filter(id=user.id).exists())
        self.assertFalse(JusPrinAICredit.objects.filter(user_id=user.id).exists())
        self.assertFalse(JusPrinChat.objects.filter(user_id=user.id).exists())
