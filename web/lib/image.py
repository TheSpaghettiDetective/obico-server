from PIL import ImageDraw

def overlay_detections(img, detections):
    draw = ImageDraw.Draw(img)
    for d in detections:
        (xc, yc, w, h) = map(int, d[2])
        draw.rectangle([(xc-w//2,yc-h//2),(xc+w//2,yc+w//2)],outline=(0,255,0,255))
    return img
