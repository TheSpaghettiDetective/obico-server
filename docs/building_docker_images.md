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
