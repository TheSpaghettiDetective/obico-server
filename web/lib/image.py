from PIL import ImageDraw, ImageStat
import math
import cv2

def overlay_detections(img, detections):
    draw = ImageDraw.Draw(img)
    for d in detections:
        (xc, yc, w, h) = map(int, d[2])
        (x1, y1), (x2, y2) = (xc-w//2,yc-h//2), (xc+w//2,yc+w//2)
        points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
        draw.line(points, fill=(0,255,0,255), width=3)
    return img

def image_too_dark(img):
    BRIGHTNESS_THRESHOLD = 40

    stat = ImageStat.Stat(img)
    r,g,b = stat.mean
    return math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2)) < BRIGHTNESS_THRESHOLD

def sharpness(img):
    focus_std = cv2.meanStdDev(cv2.Laplacian(img, cv2.CV_64F))[1]
    return focus_std * focus_std
