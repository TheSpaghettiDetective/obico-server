from django.test import RequestFactory, TestCase

from app.models import GCodeFolder, Printer, User
from api.gcode_utils import filter_by_parent_folder
from api.serializers import GCodeFileDeSerializer, GCodeFolderDeSerializer


class GCodeSerializerValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='gcode-owner@test.com')
        self.other_user = User.objects.create(email='gcode-other@test.com')
        self.parent_folder = GCodeFolder.objects.create(
            user=self.user,
            name='Parent',
            safe_name='Parent',
        )
        self.other_parent_folder = GCodeFolder.objects.create(
            user=self.other_user,
            name='Other parent',
            safe_name='Other_parent',
        )
        self.request = RequestFactory().post('/')
        self.request.user = self.user

    def serializer_context(self):
        return {'request': self.request}

    def test_folder_and_file_names_use_the_same_safe_name_rules(self):
        folder = GCodeFolderDeSerializer(
            data={'name': 'Spool #1'},
            context=self.serializer_context(),
        )
        gcode_file = GCodeFileDeSerializer(
            data={'filename': 'toolpath #1.gcode'},
            context=self.serializer_context(),
        )

        self.assertTrue(folder.is_valid(), folder.errors)
        self.assertTrue(gcode_file.is_valid(), gcode_file.errors)
        self.assertEqual(folder.validated_data['safe_name'], 'Spool__1')
        self.assertEqual(gcode_file.validated_data['safe_filename'], 'toolpath__1.gcode')

    def test_both_serializers_accept_parent_folder_owned_by_request_user(self):
        serializers = (
            GCodeFolderDeSerializer(
                data={'name': 'Child', 'parent_folder': self.parent_folder.id},
                context=self.serializer_context(),
            ),
            GCodeFileDeSerializer(
                data={'filename': 'toolpath.gcode', 'parent_folder': self.parent_folder.id},
                context=self.serializer_context(),
            ),
        )

        for serializer in serializers:
            with self.subTest(serializer=serializer.__class__.__name__):
                self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_both_serializers_reject_parent_folder_owned_by_another_user(self):
        serializers = (
            GCodeFolderDeSerializer(
                data={'name': 'Child', 'parent_folder': self.other_parent_folder.id},
                context=self.serializer_context(),
            ),
            GCodeFileDeSerializer(
                data={'filename': 'toolpath.gcode', 'parent_folder': self.other_parent_folder.id},
                context=self.serializer_context(),
            ),
        )

        for serializer in serializers:
            with self.subTest(serializer=serializer.__class__.__name__):
                self.assertFalse(serializer.is_valid())
                self.assertIn('parent_folder', serializer.errors)


class GCodeParentFolderFilterTests(TestCase):
    def setUp(self):
        user = User.objects.create(email='gcode-filter@test.com')
        self.root_folder = GCodeFolder.objects.create(
            user=user,
            name='Root',
            safe_name='Root',
        )
        self.child_folder = GCodeFolder.objects.create(
            user=user,
            name='Child',
            safe_name='Child',
            parent_folder=self.root_folder,
        )

    def test_filter_preserves_unfiltered_queryset_when_parameter_is_absent(self):
        queryset = GCodeFolder.objects.all()
        filtered = filter_by_parent_folder(queryset, {})

        self.assertQuerySetEqual(filtered, queryset, transform=lambda folder: folder.id)

    def test_filter_supports_root_and_specific_parent_queries(self):
        queryset = GCodeFolder.objects.all()
        roots = filter_by_parent_folder(queryset, {'parent_folder': 'null'})
        children = filter_by_parent_folder(
            queryset,
            {'parent_folder': str(self.root_folder.id)},
        )

        self.assertQuerySetEqual(roots, [self.root_folder.id], transform=lambda folder: folder.id)
        self.assertQuerySetEqual(children, [self.child_folder.id], transform=lambda folder: folder.id)


class PrinterAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='printer-auth@test.com')
        self.printer = Printer.objects.create(
            user=self.user,
            name='Test printer',
            auth_token='valid-token',
        )

    def test_valid_token_authenticates_as_printer_owner_and_returns_printer(self):
        from api.authentication import PrinterAuthentication

        user, printer = PrinterAuthentication().authenticate_credentials('valid-token')

        self.assertEqual(user, self.user)
        self.assertEqual(printer, self.printer)

    def test_invalid_token_fails_authentication(self):
        from rest_framework.exceptions import AuthenticationFailed

        from api.authentication import PrinterAuthentication

        with self.assertRaises(AuthenticationFailed) as error:
            PrinterAuthentication().authenticate_credentials('invalid-token')

        self.assertEqual(error.exception.detail['is_authenticated'], False)
