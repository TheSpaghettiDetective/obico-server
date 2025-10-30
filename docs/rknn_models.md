# RKNN Models

## Summary
The RKNN model weights are converted from the existing ONNX model.

The RKNN model format is hardware specific, though the runtime (and therefore, base image) are not.

## Model Conversion
RKNN-format models can be built in batch using `scripts/make_rknn_images.py`.  
This requires that the RKNN toolkit (not the lite version) is available to python (such as in a venv).  
This process need not take place on the target hardware, using a more powerful workstation is recommended.

### Basic process
(the following assumes that python 3.11 is used, adjust url and venv creation for other versions)
```shell
{
curl -L\# "$(cat model/model-weights.onnx.url)" -o model/model-weights.onnx --fail
python3.11 -m venv --upgrade-deps --prompt rknn rknn.venv 
source ./rknn.venv/bin/activate
pip install https://github.com/airockchip/rknn-toolkit2/raw/refs/heads/master/rknn-toolkit2/packages/x86_64/rknn_toolkit2-2.3.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
pip uninstall -y opencv-python
pip install opencv-python-headless
./scripts/make_rknn_images.py model/model-weights.onnx model/rknn
}
```

### Docker
```shell
{
curl -L\# "$(cat model/model-weights.onnx.url)" -o model/model-weights.onnx --fail
docker run --rm -it -v $PWD/model:/model:rw some-registry.example/rknn-toolkit:latest make_rknn_images.py /model/model-weights.onnx /model/rknn 
}
```

## Using with the provided Docker-Compose
Whenever using docker-compose, provide both `docker-compose.yml` and `docker-compose-rknn.yml`.
e.g. `docker compose -f docker-compose.yml -f docker-compose-rknn.yml up -d`

**IMPORTANT**: The RKNN docker-compose requires docker compose v2. It will not function with compose v1.


## Running in Docker
The RKNN Runtime interacts with the NPU via DRI, and determines what hardware is present by reading the devicetree.

Docker needs: `--device /dev/dri --security-opt systempaths=unconfined`

Podman needs: `--device /dev/dri --security-opt unmask=/sys/firmware`

## From scratch with docker on a RADXA Zero 3E
1. Flash an sdcard with Armbian community minimal
    https://dl.armbian.com/radxa-zero3/Bookworm_vendor_minimal
2. Repair the PMBR so that it matches the new size of the SD card
    ```shell
    # fdisk /dev/sda
    Welcome to fdisk (util-linux 2.41).
    Changes will remain in memory only, until you decide to write them.
    Be careful before using the write command.
    
    GPT PMBR size mismatch (4571135 != 61069311) will be corrected by write.
    The primary GPT table is corrupt, but the backup appears OK, so that will be used.
    
    Command (m for help): w
    
    The partition table has been altered.
    Calling ioctl() to re-read partition table.
    Syncing disks.
    ```
3. Insert the SD card into the device, and connect to network, and power it on
4. Either using a keyboard/monitor, or with ssh `root@DEVICE_IP` with password `1234`, complete the armbian initial setup
5. Log back into the zero with your newly-created user account, and download and install the enable-NPU overlay.
    ```shell
    curl -LO\# 'https://github.com/radxa-pkg/radxa-overlays/raw/refs/heads/main/arch/arm64/boot/dts/rockchip/overlays/rk3568-npu-enable.dts'
    sudo armbian-add-overlay rk3568-npu-enable.dts
    ```
6. Update software
    ```shell
    sudo apt-get update
    sudo apt-get upgrade
    ```
7. Reboot the device (`sudo reboot`)
8. Install software that will be needed to launch obico
    ```shell
    sudo apt-get update
    sudo apt-get install git docker.io apparmor-utils
    ``` 
9. Install docker compose 2
    ```shell
    curl -L\# -o /tmp/docker-compose https://github.com/docker/compose/releases/download/v2.37.1/docker-compose-linux-$(arch)
    sudo mkdir -p /usr/local/lib/docker/cli-plugins
    sudo install -m 755 /tmp/docker-compose /usr/local/lib/docker/cli-plugins
    ```
10. Grant your user access to manage docker resources
    ```shell
    sudo usermod -aG docker $(whoami)
    ```
    Log out and back in again
11. Clone the obico-server repo (shallow to save on disk space)  
    (To clone a branch other than `release` add `-b BRANCH_NAME` to the below command)
    ```shell
    git clone --depth 1 https://github.com/TheSpaghettiDetective/obico-server.git
    cd obico-server
    ```
12. Build the base image for the ml_api rknn container
    (this is currently not available on docker hub, when it is, this step may be skipped)
    ```shell
    docker build ml_api -f ml_api/Dockerfile.base_arm64_rknn -t thespaghettidetective/ml_api_base_rknn:latest
    ```
13. Build and launch the obico stack
    ```shell
    docker compose -f docker-compose.yml -f docker-compose-rknn.yml build
    docker compose -f docker-compose.yml -f docker-compose-rknn.yml up -d
    ```
14. See the [Server Configuration Guide](https://www.obico.io/docs/server-guides/configure/) for additional configuration.