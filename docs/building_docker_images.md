## Building ML backend images
To build images, you can use provided [build_images.sh](ml_api/scripts/build_images.sh) script.
It executes `docker` to build images, assign them tags and push into docker registry.
Script should be run from `ml_api` directory;

Arguments:
* -v VERSION argument should contain version number, like 1.3 or similar. It can also be `latest`
* -p PREFIX can be used to push images into a private repository or into a docker registry with a new name
* -i flag is used to help Docker work with insecure (like local private) repositories

To run local registry, use: https://docs.docker.com/registry/deploying/
Ex: `docker run -d -p 5000:5000 --restart=always --name registry registry:2`

Then to build and push into that repository, you can run:
`scripts/build_images -v 1.3 -p localhost:5000/thespaghettidetective -i`

(Takes several hours sometimes)

Then you can start a docker container (from `obico-server` directory):
`DOCKER_PREFIX=localhost:5000/thespaghettidetective VERSION=1.3 docker-compose up`

Or to run a specific backend:
`DOCKER_PREFIX=localhost:5000/thespaghettidetective VERSION=1.3 ML_RUNTIME=onnx ML_PROCESSOR=gpu docker-compose up`

I.e. running a simple `docker-compose up -d` will run `darknet` + `cpu` `latest` version from docker.io 


