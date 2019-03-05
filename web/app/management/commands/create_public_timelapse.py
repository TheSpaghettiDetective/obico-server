#!/usr/bin/env python
from os import path
import json
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import PublicTimelapse
from lib.file_storage import save_file_obj

class Command( BaseCommand ):
    help = 'Create PublicTimeLpase using video and p json'

    def add_arguments(self, parser):
        parser.add_argument('timelapse', type=str)
        parser.add_argument('poster', type=str)
        parser.add_argument('p_json', type=str)
        parser.add_argument('creator', type=str)

    def handle(self, *args, **options):
        timelapse_path = options['timelapse']
        poster_path = options['poster']
        p_json_path = options['p_json']
        creator = options['creator']

        tl_basename = path.basename(timelapse_path)
        post_basename = path.basename(poster_path)

        with open(timelapse_path, 'rb') as tl_file:
            _, tl_url = save_file_obj(tl_basename, tl_file, settings.TIMELAPSE_CONTAINER)

        with open(poster_path, 'rb') as poster_file:
            _, poster_url = save_file_obj(post_basename, poster_file, settings.TIMELAPSE_CONTAINER)

        with open(p_json_path, 'r') as f:
            frame_p = json.load(f)

        if len(PublicTimelapse.objects.filter(title=tl_basename)) == 1:
            PublicTimelapse.objects.filter(title=tl_basename).update(video_url=tl_url, poster_url=poster_url, creator_name=creator, frame_p=frame_p)
        else:
            PublicTimelapse.objects.create(title=tl_basename, video_url=tl_url, poster_url=poster_url, creator_name=creator, frame_p=frame_p)
