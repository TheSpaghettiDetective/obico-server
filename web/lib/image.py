from PIL import ImageDraw, ImageStat
import math
import cv2
import numpy

def overlay_detections(img, detections):
    draw = ImageDraw.Draw(img)
    for d in detections:
        (xc, yc, w, h) = map(int, d[2])
        (x1, y1), (x2, y2) = (xc-w//2,yc-h//2), (xc+w//2,yc+w//2)
        points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
        draw.line(points, fill=(0,255,0,255), width=3)
    return img

def brightness(img):
    """
    https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python

    Returns: 0 - Bright enough
             1 - Too dark
    """

    BRIGHTNESS_THRESHOLD = 40

    stat = ImageStat.Stat(img)
    r,g,b = stat.mean
    if math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2)) < BRIGHTNESS_THRESHOLD:
        return 1
    return 0


def sharpness(img):
    """
    https://stackoverflow.com/questions/7765810/is-there-a-way-to-detect-if-an-image-is-blurry

    Returns: 0 - Sharp enough
             1 - Somewhat blurry.
             2 - Too blurry to detect
    """

    SHARPNESS_THRESHOLD_1 = 30
    SHARPNESS_THRESHOLD_2 = 15

    stddev = sum(cv2.meanStdDev(cv2.Laplacian(cv2.resize(numpy.array(img), (416,416)), cv2.CV_64F))[1])[0]
    if stddev < SHARPNESS_THRESHOLD_2:
        return 2
    if stddev < SHARPNESS_THRESHOLD_1:
        return 1
    return 0
