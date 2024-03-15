from PIL import ImageDraw

def overlay_detections(img, detections):
    draw = ImageDraw.Draw(img)
    for d in detections:
        (xc, yc, w, h) = map(int, d[2])
        (x1, y1), (x2, y2) = (xc-w//2,yc-h//2), (xc+w//2,yc+h//2)
        points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
        draw.line(points, fill=(0,255,0,255), width=3)
    return img
