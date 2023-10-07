from django.urls import path

from . import views

media_patterns = [
    path(f'{TIMELAPSE_CONTAINER}/private/<str:file_name>', views.serve_timelapse_mp4),
    path(f'{PICS_CONTAINER}/ff_printshots/<int:user_id>/<int:print_id>/<str:file_name>', views.serve_media),
    path(f'{PICS_CONTAINER}/p/<int:user_id>/<str:file_name>', views.serve_media),
    path(f'{PICS_CONTAINER}/snapshots/<int:user_id>/<str:file_name>', views.serve_media),
    path(f'{PICS_CONTAINER}/raw/<int:user_id>/<str:file_name>', views.serve_media),
    path(f'{PICS_CONTAINER}/tagged/<int:user_id>/<str:file_name>', views.serve_media),
    path(f'{GCODE_CONTAINER}/<int:user_id>/<str:file_name>', views.serve_media),
    path('<path:file_path>', views.server_media_catchall),  # catchall view throws error for unauthed media requests
]
