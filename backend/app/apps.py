from channels_presence.apps import RoomsConfig
from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'


class CustomRoomsConfig(RoomsConfig):
    name = 'channels_presence'
