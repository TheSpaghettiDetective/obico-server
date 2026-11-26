# Use Obico's failure detection in your own project

This folder is Obico's failure-detection server. It is a small web server: you send it the address of a webcam snapshot, and it answers with the places in that picture where it sees a failing 3D print (spaghetti, blobs, detached parts). It needs nothing else from Obico: no database, no account, no internet connection once it is running.

Obico itself uses this server for every printer it watches. Many other projects run it on its own too, see [Built on Obico detection](#built-on-obico-detection).

## Run it

```bash
docker run -d --name obico-ml-api -p 3333:3333 ghcr.io/thespaghettidetective/obico-ml-api-cpu:release
```

The model loads in a few seconds. When `curl http://localhost:3333/hc/` prints `ok`, the server is ready.

Then ask it about a snapshot:

```bash
curl -G http://localhost:3333/p/ --data-urlencode "img=http://192.168.1.50/webcam/?action=snapshot"
```

The image has the model weights built in, so it never downloads anything at startup.

### Which image

All images are built from this folder on every Obico release and published to GitHub's container registry. The `release` tag always points at the newest one. Each release also gets a date tag, such as `2026.11.22`, which never moves; use that if you want to choose when to upgrade.

| Image | Hardware | Notes |
|---|---|---|
| `ghcr.io/thespaghettidetective/obico-ml-api-cpu` | Any 64-bit x86 or ARM computer (amd64, arm64), such as a Raspberry Pi 4 or 5 on a 64-bit OS | The one most projects want. About 650 MB. |
| `ghcr.io/thespaghettidetective/obico-ml-api-gpu` | x86 computer with an NVIDIA GPU | Needs the NVIDIA container toolkit and `--gpus all`. See [NVIDIA GPU](https://obico.io/docs/server-guides/advanced/nvidia-gpu/). |
| `ghcr.io/thespaghettidetective/obico-ml-api-jetson` | NVIDIA Jetson | Built on NVIDIA's L4T TensorRT r8.0.1 base. |

Intel GPUs and Rockchip RK3588 boards are supported from source: build `Dockerfile.intel` (see [Intel GPU](https://obico.io/docs/server-guides/advanced/intel-gpu/)) or `Dockerfile` on the RK3588 base described in the main [README](../README.md).

### Hardware

On the CPU image, one snapshot takes about 0.15 seconds on an Apple M2 Pro once the server is warm. The first request after startup is slower, about 0.7 seconds. Small ARM boards are several times slower than that. The server uses about 400 MB of memory.

The server runs one worker and handles one snapshot at a time. Obico checks each printer about once every 10 seconds, so one CPU server keeps up with several printers. For many printers, run more containers behind a load balancer, or use the GPU image.

### Options

Set these with `docker run -e NAME=value`:

- `ML_API_TOKEN`: when set, every request to `/p/` must carry the header `Authorization: Bearer <token>`, or it gets `401`. Use it if the server is reachable by anyone other than you. `/hc/` stays open.
- `SENTRY_DSN`: send errors to your own [Sentry](https://sentry.io) project.

## The API

### `GET /p/?img=<snapshot url>`

`img` is the address of a JPEG or PNG image, URL-encoded. The server downloads the picture itself, so the address must be reachable from inside the container. It gives the camera 0.1 seconds to accept the connection and 5 seconds to send the picture. If the camera is on the Docker host itself, use `host.docker.internal` as the host name (on Linux, add `--add-host=host.docker.internal:host-gateway` to `docker run`).

There is no upload endpoint. If your snapshots are not already at an address, serve them from a small web server your project runs.

An optional `X-Deadline` header holds a Unix timestamp in seconds. If that moment passes before the answer is ready, the server gives up and returns `503` with no detections, instead of holding the worker. Obico uses it so a slow camera does not delay the next printer's check.

A response looks like this:

```json
{
  "detections": [
    ["failure", 0.574, [2212.7, 1361.6, 329.7, 354.0]],
    ["failure", 0.434, [2622.7, 2236.0, 241.2, 331.9]]
  ]
}
```

Each detection is one box around something that looks like a failure:

1. The label, always `failure`.
2. The confidence, from 0 to 1. The server leaves out boxes below 0.08.
3. The box as `[center x, center y, width, height]`, in pixels of the picture you sent.

A picture with nothing wrong in it returns `{"detections": []}`.

| Status | Meaning |
|---|---|
| `200` | The picture was checked. `detections` may be empty. |
| `400` | The picture could not be downloaded or read, or `X-Deadline` is not a number. `message` says why. |
| `401` | `ML_API_TOKEN` is set and the request did not carry it. |
| `422` | The request had no `img` parameter. |
| `503` | `X-Deadline` passed before the answer was ready. |

### `GET /hc/`

Returns `ok` when the model is loaded. Use it as the container's health check.

## What the scores mean, and when to alert

One box is weak evidence. Lighting, a busy background or a purge line can each produce a box now and then. Obico never alerts on a single snapshot. It watches the trend over many of them, and the numbers below are the ones it uses, tuned on years of real prints at one snapshot every 10 seconds.

For each snapshot, add up the confidences of all its boxes. Call that the snapshot's score. On the CPU image, a photo of a print that had clearly turned into spaghetti scored about 7.5 across 28 boxes, and a photo of a good first layer scored 0. The darknet model in the GPU image gives somewhat different numbers for the same photo, so tune any threshold of your own on the image you run.

Then, for each print:

1. Ignore the first 30 snapshots (about 5 minutes). The start of a print, with a purge line and an empty bed, is easy to misread.
2. Keep a smoothed score: an exponentially weighted average of the snapshot scores with a span of 12 snapshots (each new score gets a weight of 2/13).
3. Keep a long-run average of the scores for this camera, over about the last 7,200 snapshots (20 hours of printing). It is the camera's normal level, the score it reads even when nothing is wrong. Subtract it from the smoothed score.
4. If what is left is below 0.38, the print looks fine. Above 0.78, warn the user. In between, warn if it is also more than 3.8 times this print's own recent level (the average over its last 310 snapshots, minus the long-run average).
5. Pause the printer only when the score is 1.75 times what it takes to warn.

Obico's own code for this is short: [`backend/lib/prediction.py`](../backend/lib/prediction.py) holds the steps above, and the numbers are `FD_1ST_GEN_PARAMS` in [`backend/config/settings.py`](../backend/config/settings.py). Obico also lets each user scale the score by a sensitivity setting, from about 0.8 (fewer alerts) to 1.2 (more alerts).

If you want something simpler to start with: snapshot every 10 seconds, smooth the score as in step 2, and alert when the smoothed score stays above about 0.8 for a minute. Expect more false alarms than Obico gives, mostly at the start of prints and on cameras with busy backgrounds.

## The model files

The images already contain the model, so most projects never need these. If you run inference yourself, the files are attached to the [ml-models-2026-11-23 release](https://github.com/TheSpaghettiDetective/obico-server/releases/tag/ml-models-2026-11-23) of this repository:

| File | Format | SHA-256 |
|---|---|---|
| `model-weights-5a6b1be1fa.onnx` | ONNX, for ONNX Runtime | `0a6ebd8e30dbf6a450c50f9c0a5406f04ba7eb1c99fd5996e888c78bb383b9aa` |
| `model-weights-ef79dacfd0051ab526f3002d5f5f9912.darknet` | Darknet weights, used with [`model/model.cfg`](model/model.cfg) | `3e6f7e3f166aa3a0ac08620949df71df853ac4b63af537f116be604bba54b292` |

The current addresses are always in [`model/model-weights.onnx.url`](model/model-weights.onnx.url) and [`model/model-weights.darknet.url`](model/model-weights.darknet.url), with checksums in the `.sha256` file next to each one. The input size, anchors and post-processing are in [`lib/onnx.py`](lib/onnx.py).

Each file is about 200 MB. Download it once and keep it, for example in a volume or in your own image. Please don't download it again every time your program or test suite starts.

## License

The server and the model are part of obico-server and are released under the [GNU Affero General Public License v3.0](../LICENSE) (AGPL-3.0). Read the license before you build on it. In short, if you change this code or model and let people use your changed version over a network, you have to offer them its source too.

## Built on Obico detection

These projects run this server or its model to watch printers. Thank you for building on it.

- [Bambuddy](https://github.com/maziggy/bambuddy): self-hosted command center for Bambu Lab printers.
- [Bambu Lab P1 spaghetti detection for Home Assistant](https://github.com/nberktumer/ha-bambu-lab-p1-spaghetti-detection), by nberktumer.
- [Elegoo spaghetti detection for Home Assistant](https://github.com/hepter/ha-elegoo-spaghetti-detection), by hepter.
- [Pygmy](https://github.com/danderik88/pygmy): Bambu Lab and Klipper printers from your phone.
- [BamDude](https://github.com/kainpl/bamdude): print archive and management for Bambu Lab printers.
- [Spooler](https://github.com/tharje/spooler-v2): dashboard for Elegoo Centauri Carbon printers.
- [Failed 3D prints bot](https://github.com/antirez/failed-3d-prints-bot): a Telegram bot that sends you a picture when a print fails.
- [Obico ML Home Assistant add-on](https://github.com/nobodyguy/obico_ml_ha_addon), by nobodyguy.
- [P1S AI print monitor for Home Assistant](https://github.com/Aleksusss/ha-p1s-ai-print-monitor), by Aleksusss.
- [PrintFarmer](https://github.com/OlyForge3D/PrintFarmer): print farm management.
- [Print Handy](https://github.com/catduckgnaf/print-handy): slices models sent from Discord, Telegram or Matrix, and watches the camera for failed prints.
- [print-guard](https://github.com/Servation/print-guard): Windows program that watches a Bambu Lab P1S camera and pauses failing prints.
- [PrintView](https://github.com/wvfouram/printview): Raspberry Pi 5 service for a Bambu Lab P1S, with local spaghetti detection and timelapses.
- [bambu-print-guard](https://github.com/noskillor/bambu-print-guard): Home Assistant automation that sends a photo of the failure when a Bambu Lab print goes wrong.

If your project uses Obico's detection, please link back to this page from your README, for example "Failure detection by [Obico](https://github.com/TheSpaghettiDetective/obico-server/tree/release/ml_api)", and open a pull request adding yourself to this list.

Questions and ideas are welcome in [GitHub issues](https://github.com/TheSpaghettiDetective/obico-server/issues) or on [Discord](https://obico.io/discord).
