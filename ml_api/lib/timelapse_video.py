import sys, os
import cv2
from os import path
import json
import glob

from lib.detection_model import load_net, detect
from lib.session_agg import predict

def sum_score(detections):
        return sum([d[1] for d in detections])

def overlay_detections(img, detections):
    for d in detections:
        score = '%.2f' % d[1]
        (xc, yc, w, h) = map(int, d[2])
        img = cv2.rectangle(img,(xc-w//2,yc-h//2),(xc+w//2,yc+w//2),(0,255,0),3)
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #img = cv2.putText(img,score,(xc-w//2,yc-h//2-10), font, 1,(255,0,0),3,cv2.LINE_AA)
    return img

def video_detect(jpgs_path, save_frame_to=None, weights_path=path.join(path.dirname(__file__), "..", "model", "model.weights"), thresh=0.25):
    cfg_path = path.join(path.dirname(__file__), "..", "model", "model.cfg")
    meta_path = path.join(path.dirname(__file__), "..", "model", "model.meta")
    net_main, meta_main = load_net(cfg_path, weights_path, meta_path)

    if save_frame_to:
        if not path.exists(save_frame_to):
            os.makedirs(save_frame_to)

    jpg_files = sorted(glob.glob(path.join(jpgs_path, '*.jpg')))
    result = []
    session = {}
    for idx, jpg_file in enumerate(jpg_files):
        custom_image_bgr = cv2.imread(jpg_file)
        detections = detect(net_main, meta_main, custom_image_bgr, thresh=thresh)
        img_file = "%05d.jpg" % idx
        if save_frame_to:
            cv2.imwrite(path.join(save_frame_to, img_file), overlay_detections(custom_image_bgr, detections))

        p, session = predict(detections, session)

        result += [dict(frame=idx, p=p, detections=detections)]

    if save_frame_to:
        with open(path.join(save_frame_to, 'detections.json'), 'w') as outfile:
            json.dump(result, outfile)

    return result

if __name__ == "__main__":
    video_detect(sys.argv[1], save_frame_to=sys.argv[2], weights_path=sys.argv[3], thresh=float(sys.argv[4]))

