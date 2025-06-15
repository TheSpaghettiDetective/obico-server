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
e.g. `docker-compose -f docker-compose.yml -f docker-compose-rknn.yml up -d`


## Running in Docker
The RKNN Runtime interacts with the NPU via DRI, and determines what hardware is present by reading the devicetree.

Docker needs: `--device /dev/dri --security-opt systempaths=unconfined`

Podman needs: `--device /dev/dri --security-opt unmask=/sys/firmware`