---
title: Running Obico Server with AMD GPU acceleration
---

:::tip
Experimental. AMD acceleration is currently available on Linux hosts with an AMD GPU supported by the ROCm release the image pins (see the list below). The image targets amd64 hosts.
:::

AMD acceleration uses the [MIGraphX execution provider](https://onnxruntime.ai/docs/execution-providers/MIGraphX-ExecutionProvider.html) — ONNX Runtime built against ROCm and shipped by AMD as a separate distribution (`onnxruntime-migraphx`). Because that wheel replaces the plain `onnxruntime` package, AMD ships as its own image (`Dockerfile.amd`, published as the `amd-*` tags) rather than a setting on the CUDA or CPU images.

## Supported GPUs {#supported-gpus}

The image pins the ROCm 7.2.1 runtime, so a GPU is only accelerated if that ROCm release has kernels for it:

| GPU | Architecture | Obico AMD image |
|:---|:---|:---|
| Radeon RX 6000 series | `gfx1030` | Supported |
| Radeon RX 7000 series | `gfx1100` / `gfx1101` / `gfx1102` | Supported |
| Radeon RX 9000 series | `gfx1200` / `gfx1201` | Supported |
| Radeon PRO / AMD Instinct | workstation & datacenter SKUs | Supported |
| Ryzen AI Max 300-series (and other AMD APUs whose iGPU is listed in the [ROCm compatibility matrix](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibilitymatrix/lin/releasenotes_radeon_ryzen_compatibility_matrix.html)) | e.g. `gfx1151` | Supported |
| Ryzen 3000G / 4000G / 5000G iGPU (Renoir / Cezanne) | `gfx90c` | **Not supported** — use the CPU image |

In short: discrete Radeon RX 6000 and newer, and Ryzen's AI Max-class APUs, are the target hardware. Older Ryzen iGPUs are not covered by current ROCm kernels — see [Unsupported GPUs](#unsupported-gpus) for what happens if you try, and why CPU is the better choice for them anyway.

## Host requirements {#host-requirements}

- A Linux host running the `amdgpu` kernel driver with KFD enabled. The host does **not** need ROCm installed — the image carries its own ROCm user-space — but it does expose `/dev/kfd` and `/dev/dri`. Check with:

  ```bash
  ls -l /dev/kfd /dev/dri
  ```

  If they are missing, load/enable the `amdgpu` driver (for an iGPU, the BIOS may need `iGPU` + `Above 4G decoding` enabled). Docker must be able to pass these devices, and the user running Docker needs access to the `render` group (or run Docker as root).

- A recent kernel / distro (Ubuntu 22.04+, 24.04 recommended) that already runs the `amdgpu` driver for your card.

## Start the AMD image {#start-the-amd-image}

In the host shell (bash/zsh):

```bash
docker compose -f docker-compose.yml -f docker-compose.amd.yml up -d
```

`docker-compose.amd.yml` builds the ML service from `ml_api/Dockerfile.amd`, requests the MIGraphX provider (`ML_API_GPU_PROVIDER=MIGraphXExecutionProvider`, optional `ML_API_MIGRAPHX_DEVICE_ID`) and passes `/dev/kfd` and `/dev/dri` into the container.

## Confirm GPU inference {#confirm-gpu-inference}

Run:

```bash
docker compose logs ml_api
```

You should see:

```text
ONNX Runtime execution providers: ['MIGraphXExecutionProvider', 'CPUExecutionProvider']
```

If `MIGraphXExecutionProvider` is missing, the ML container raises an error rather than silently falling back to CPU. If the container does not start at all, it is most likely a host driver/device problem: check `/dev/kfd` permissions, the `amdgpu` driver, and your user's access to the `render` group.

Before committing to the AMD image, you can probe your GPU with the same runtime the image uses:

```bash
docker compose -f docker-compose.yml -f docker-compose.amd.yml build ml_api
docker run --rm \
  --device /dev/kfd --device /dev/dri \
  "$(docker compose -f docker-compose.yml -f docker-compose.amd.yml ps -q ml_api | xargs docker inspect -f '{{.Image}}')" \
  python -u -c "
import onnxruntime as o
s = o.InferenceSession('/model_cache/ml_api/onnx/model-weights.onnx',
    providers=[('MIGraphXExecutionProvider', {'device_id': '0'}), 'CPUExecutionProvider'])
print('assigned providers:', s.get_providers())
"
```

A supported GPU prints `assigned providers: ['MIGraphXExecutionProvider', 'CPUExecutionProvider']` after loading the real model.

## Unsupported GPUs {#unsupported-gpus}

On GPUs without ROCm kernels the runtime aborts at model load — there is no graceful CPU fallback inside the AMD image. Field-tested on a Ryzen 5700G (`gfx90c` iGPU): the MIGraphX provider is assigned, then the first inference dies with

```text
rocBLAS error: Cannot read TensileLibrary.dat: Illegal seek for GPU arch :
gfx90c
```

followed by a segfault (exit 139).

The deprecated ROCm execution provider (last available in ONNX Runtime 1.21 / ROCm 6.4) was tested on the same card: it assigns `ROCMExecutionProvider` fine, but the first inference hits the identical missing-kernels wall, and forcing `HSA_OVERRIDE_GFX_VERSION=9.0.8` aborts with `HSA_STATUS_ERROR_ILLEGAL_INSTRUCTION` (the `gfx908` kernels use CDNA/Matrix cores that Vega iGPUs do not have).

For these older APUs the CPU is also simply faster: measured on the same Ryzen 5700G, this model runs in ~38 ms on 8 CPU cores (~66 ms when limited to 4) versus ~201 ms through the iGPU via WebGPU. Keep the standard CPU image — it wins on both speed and reliability for `gfx90c`-class hardware.
