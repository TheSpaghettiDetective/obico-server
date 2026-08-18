from typing import Callable, List

from app.models import Print, PrinterEvent, GCodeFile, models, PrintShotFeedback


# All model fields that hold media URLs (timelapses, snapshots, thumbnails, etc.)
MEDIA_URL_FIELDS = [
    (GCodeFile, ['url', 'thumbnail1_url', 'thumbnail2_url', 'thumbnail3_url']),
    (Print, ['video_url', 'tagged_video_url', 'poster_url', 'prediction_json_url']),
    (PrinterEvent, ['image_url']),
    (PrintShotFeedback, ['image_url']),
]


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


def transform_urls_on_model(obj: models.Model, url_fields: List[str], transform: Callable[[str], str], save: bool = True) -> int:
    """
    Applies `transform` to every non-empty URL field on every row of `obj`, saving each
    row that changed. Returns the number of URLs that were changed. With save=False,
    nothing is written but the count is still returned (for dry runs).
    """
    changed_urls = 0
    total_rows = len(obj.objects.all())
    for idx, row in enumerate(obj.objects.all()):
        changed = False
        for url_field in url_fields:
            url = getattr(row, url_field)
            if url:
                new_url = transform(url)
                if new_url != url:
                    setattr(row, url_field, new_url)
                    changed = True
                    changed_urls += 1
        if changed and save:
            row.save()
        if idx % 20 == 0:
            print_progress_bar(idx + 1, total_rows)
    print_progress_bar(1, 1)
    return changed_urls
