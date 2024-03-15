from typing import List

from django.core.management.base import BaseCommand

from app.models import Print, PrinterEvent, GCodeFile, models, PrintShotFeedback
from lib.url_signing import new_signed_url


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
def print_progress_bar(iteration, total, prefix='Progress:', suffix='Complete', decimals=1, length=50, fill='X', printEnd=""):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd, flush=True)
    # Print New Line on Complete
    if iteration == total:
        print()

class Command(BaseCommand):
    help = '(re-)signs all media URLs. Must be run once after updating, and any time the Django SECRET_KEY is rotated'

    @staticmethod
    def _resign_urls_on_model(obj: models.Model, url_fields: List[str]):
        changed = False
        total_rows = len(obj.objects.all())
        print(f"Resigning {obj.__name__} URLs ({total_rows} rows)...")
        for idx, row in enumerate(obj.objects.all()):
            for url_field in url_fields:
                url = getattr(row, url_field)
                if url:
                    setattr(row, url_field, new_signed_url(url))
                    changed = True
            if changed:
                row.save()
            if idx % 20 == 0:
                print_progress_bar(idx + 1, total_rows)
        print_progress_bar(1, 1)

    def resign_urls(self):
        self._resign_urls_on_model(
            obj=GCodeFile,  # type: ignore
            url_fields=['url', 'thumbnail1_url', 'thumbnail2_url', 'thumbnail3_url']
        )
        self._resign_urls_on_model(
            obj=Print,  # type: ignore
            url_fields=['video_url', 'tagged_video_url', 'poster_url', 'prediction_json_url']
        )
        self._resign_urls_on_model(
            obj=PrinterEvent,  # type: ignore
            url_fields=['image_url']
        )
        self._resign_urls_on_model(
            obj=PrintShotFeedback,  # type: ignore
            url_fields=['image_url']
        )

    def handle(self, *args, **options):
        self.resign_urls()
