#!/bin/bash -e

TL_FILE=$1
OUT_DIR=$2

TL_BN=$(basename "$TL_FILE")

JPG_IN_DIR="/tmp/in/$TL_BN"
JPG_OUT_DIR="/tmp/out/$TL_BN"
rm -rf "$JPG_IN_DIR"
mkdir -p "$JPG_IN_DIR"
rm -rf "$JPG_OUT_DIR"
mkdir -p "$JPG_OUT_DIR"

FRM_NUM=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 "$TL_FILE")

if [ $FRM_NUM -gt 750 ]; then
    FPS=$((25*750/$FRM_NUM))
else
    FPS=25
fi

ffmpeg -i "$TL_FILE" -vf fps=$FPS -qscale:v 2 "$JPG_IN_DIR/%5d.jpg"

python -m lib.timelapse_video "$JPG_IN_DIR" "$JPG_OUT_DIR" model/model.weights 0.25

ffmpeg -i "$JPG_OUT_DIR/%05d.jpg" -c:v libx264 -vf fps=25 -pix_fmt yuv420p "$OUT_DIR/$TL_BN"
cp "$JPG_OUT_DIR/detections.json" "$OUT_DIR/$TL_BN.json"
cp "$JPG_OUT_DIR/00001.jpg" "$OUT_DIR/$TL_BN.poster.jpg"

rm -rf "$JPG_IN_DIR"
rm -rf "$JPG_OUT_DIR"
