import io
import logging
import json
import requests
from django.conf import settings
from PIL import Image

from lib.file_storage import save_file_obj
from lib import cache
from lib.image import overlay_detections
from lib.utils import ml_api_auth_headers
from lib.prediction import update_prediction_with_detections, is_failing, VISUALIZATION_THRESH
from app.models import PrinterPrediction

LOGGER = logging.getLogger(__name__)

IMG_URL_TTL_SECONDS = 60 * 30


def save_detection_artifacts(printer, pic, pic_id, detections, prediction_state, visualization_thresh):
    """
    Shared function to save detection artifacts (tagged image and prediction JSON).

    Args:
        printer: Printer model instance
        pic: Image file object
        pic_id: Unique identifier for this image (timestamp string)
        detections: List of [box, confidence] pairs
        prediction_state: Dict with prediction state (current_p, ewm_mean, etc.)
        visualization_thresh: Threshold for drawing detection boxes

    Returns:
        str: URL of the tagged image
    """
    # Create tagged image with detection overlays
    pic.file.seek(0)
    tagged_img = io.BytesIO()
    detections_to_visualize = [d for d in detections if d[1] > visualization_thresh]
    overlay_detections(Image.open(pic.file), detections_to_visualize).save(tagged_img, "JPEG")
    tagged_img.seek(0)

    pic_path = f'tagged/{printer.id}/{printer.current_print.id}/{pic_id}.jpg'
    _, tagged_img_url = save_file_obj(
        pic_path, tagged_img, settings.PICS_CONTAINER,
        printer.user.syndicate.name, long_term_storage=False
    )

    # Save prediction state as JSON
    prediction_json = json.dumps(prediction_state)
    p_out = io.BytesIO()
    p_out.write(prediction_json.encode('UTF-8'))
    p_out.seek(0)
    save_file_obj(
        f'p/{printer.id}/{printer.current_print.id}/{pic_id}.json',
        p_out, settings.PICS_CONTAINER,
        printer.user.syndicate.name, long_term_storage=False
    )

    return tagged_img_url


def detect(printer, pic, pic_id, raw_pic_url):
    """
    Perform failure detection using 1st generation model (ML API /p/ endpoint).

    Args:
        printer: Printer model instance
        pic: Image file object
        pic_id: Unique identifier for this image (timestamp string)
        raw_pic_url: URL of the raw image stored in cloud

    Returns:
        dict: {
            'model': 'fd_1st_gen',
            'detections': list of detection results [[box_coords, confidence], ...],
            'decision': {
                'should_pause': bool,
                'should_alert': bool,
            },
        }
    """
    prediction, _ = PrinterPrediction.objects.get_or_create(printer=printer)

    # Call ML API for detection
    req = requests.get(
        settings.ML_API_HOST + '/p/',
        params={'img': raw_pic_url},
        headers=ml_api_auth_headers(),
        verify=False
    )
    req.raise_for_status()
    detections = req.json()['detections']

    if settings.DEBUG:
        LOGGER.info(f'Detections: {detections}')

    # Update prediction statistics (1st gen algorithm)
    update_prediction_with_detections(prediction, detections, printer)
    prediction.save()

    # Track high predictions for focused feedback
    if prediction.current_p > settings.THRESHOLD_LOW * 0.2:
        cache.print_high_prediction_add(printer.current_print.id, prediction.current_p, pic_id)

    # Build prediction state dict for artifact saving
    prediction_state = {
        'current_p': prediction.current_p,
        'current_frame_num': prediction.current_frame_num,
        'lifetime_frame_num': prediction.lifetime_frame_num,
        'ewm_mean': prediction.ewm_mean,
        'rolling_mean_short': prediction.rolling_mean_short,
        'rolling_mean_long': prediction.rolling_mean_long,
    }

    # Save artifacts (shared function)
    tagged_img_url = save_detection_artifacts(
        printer, pic, pic_id, detections, prediction_state, VISUALIZATION_THRESH
    )

    # Update cached image URL
    cache.printer_pic_set(printer.id, {'img_url': tagged_img_url}, ex=IMG_URL_TTL_SECONDS)

    # Determine failure decision (1st gen algorithm)
    should_pause = is_failing(
        prediction,
        printer.detective_sensitivity,
        escalating_factor=settings.ESCALATING_FACTOR
    )
    should_alert = not should_pause and is_failing(
        prediction,
        printer.detective_sensitivity,
        escalating_factor=1
    )

    return {
        'model': 'fd_1st_gen',
        'detections': detections,
        'decision': {
            'should_pause': should_pause,
            'should_alert': should_alert,
        },
        'tagged_img_url': tagged_img_url,
    }
