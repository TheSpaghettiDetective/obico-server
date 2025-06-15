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
1. Before building, ensure that the correct RKNN model for your target hardware is present at `model/model-weights.rknn`
2. Modify the ml_api compose configuration to change the dockerfile used when building
    ```diff
         restart: unless-stopped
         build:
           context: ml_api
    +      dockerfile: Dockerfile.rknn
    ```
3. docker-compose build ml_api

If you are going to run on the same machine, see the note below about arguments for docker/podman about arguments.

## Running in Docker
Note that the RKNN library reads the firmware device tree to determine what hardware is in use.

Docker needs: `--device /dev/dri --security-opt systempaths=unconfined`

Podman needs: `--device /dev/dri --security-opt unmask=/sys/firmware`