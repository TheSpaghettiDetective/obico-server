---
title: Running Obico Server with Intel GPU acceleration
---

:::tip
This is available on Linux hosts with an Intel integrated GPU or Intel Arc
GPU. The Intel image currently targets amd64 hosts.
:::

## Host requirements

Install a supported Intel graphics kernel driver and firmware on the host. For
Intel Arc, use a recent Linux kernel; OpenVINO recommends kernel 6.2 or newer
for Arc GPUs. The supplied container installs the OpenCL and Level Zero
user-space runtime, so those packages do not need to be installed on the host.
Ensure the account that runs Docker can access the render device:

```bash
sudo usermod -aG render "$USER"
```

Log out and back in after changing group membership. Verify that a render
device exists:

```bash
ls -l /dev/dri/render*
```

The host driver and container runtime are separate: the host provides the
kernel device, while the Intel ML image contains the user-space OpenVINO GPU
runtime. The container needs `/dev/dri` passed through, which the supplied
Compose file does.

## Start the Intel image

From the repository root, run:

```bash
docker compose -f docker-compose.yml -f docker-compose.intel.yml up -d --build
```

The override builds `ml_api/Dockerfile.intel`, selects the OpenVINO execution
provider, and passes `/dev/dri` into the `ml_api` container. It is deliberately
an explicit override so a normal `docker compose up` keeps the existing CUDA
deployment behavior.

## Confirm GPU inference

Inspect the ML API logs:

```bash
docker compose logs ml_api
```

A successful Intel load includes:

```
ONNX Runtime execution providers: ['OpenVINOExecutionProvider', 'CPUExecutionProvider']
----- Trying to load weights: /model_cache/ml_api/onnx/model-weights.onnx - use_gpu = True -----
Succeeded!
```

If the OpenVINO GPU cannot initialize, the loader retries the same ONNX model
with `CPUExecutionProvider`. Check `/dev/dri` permissions and the host Intel
driver in that case.

The provider can target a particular Intel GPU or tile by creating a local
Compose override with, for example, `ML_API_OPENVINO_DEVICE: GPU.1`.
