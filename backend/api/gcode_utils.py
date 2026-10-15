import re

from rest_framework import serializers


def safe_gcode_name(name):
    return re.sub(r'[^\w\.]', '_', name)


class GCodeParentFolderValidationMixin:
    def validate_parent_folder(self, parent_folder):
        if parent_folder is not None and self.context['request'].user != parent_folder.user:
            raise serializers.ValidationError('Parent folder does not exist')
        return parent_folder


def filter_by_parent_folder(queryset, query_params):
    if 'parent_folder' not in query_params:
        return queryset

    parent_folder = query_params.get('parent_folder')
    if parent_folder == 'null' or parent_folder == '':
        return queryset.filter(parent_folder__isnull=True)
    return queryset.filter(parent_folder_id=int(parent_folder))
