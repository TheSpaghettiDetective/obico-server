---
title: Hardware requirements
---

The Obico Server runs a powerful Machine Learning model that requires a device powerful enough to run it. And by powerful, we mean most anything from the last decade.

## Single Board Computers {#single-board-computers}

:::info
This is an incomplete list. Only tested / known devices are included.
:::

Device | Can run Obico
:---|:---:
Raspberry Pi (any model) | ❌
Latte Panda | ❌
Jetson Nano 2gb | ❌
Jetson Nano 4gb | ✅

## PC's (and laptops) {#pcs-and-laptops}

If it has at least 4gb of RAM, it should run fine.

Component | Requirement
:---|:---
CPU | One that can run a modern OS. CPU's as old as 4th Gen Intel have been able to run Obico just fine.
GPU | Optional. NVIDIA CUDA and Intel OpenVINO acceleration are supported on Linux hosts; see the GPU guides below.
RAM | You should have at least 4gb of DDR3 ram, but the more the better.
OS | Either Windows, Linux, or MacOS X will work. The OS version should be recent enough to run Docker. For older devices, Linux is **highly** recommended.
RGB | Highly recommended. The more your PC looks like a christmas tree, the more FPS you will have (sarcasm)

## GPU acceleration {#gpu-acceleration}

GPU acceleration is optional. CPU inference works on all supported platforms, while GPU acceleration currently requires a Linux host:

- [NVIDIA GPU with CUDA](advanced/nvidia-gpu.md)
- [Intel GPU with OpenVINO](advanced/intel-gpu.md)

AMD GPU acceleration is not currently included in the Docker Compose images. ROCm support varies by GPU model, operating system, and runtime version; an AMD/MIGraphX image can be added separately once it has been validated.
