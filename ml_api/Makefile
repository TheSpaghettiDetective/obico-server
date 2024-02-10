GIT_COMMIT := $(shell git rev-parse --short HEAD)
GIT_SOURCE := $(shell git config --get remote.origin.url)
QUAY_REPO_USER := kaszpir
QUAY_REPO_NAME := ml_api

help:
	@grep -E '(^[0-9a-zA-Z_-]+:.*?##.*$$)|(^##)' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

version: ## show git version
	@echo GIT_COMMIT IS $(GIT_COMMIT)

lint-dockerfile: ## Runs hadolint against application dockerfile
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint Dockerfile.base_amd64
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint Dockerfile.base_arm64
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint Dockerfile

docker_config: ## configure docker to allow multi-arch builds
	docker run --privileged --rm tonistiigi/binfmt --install all

ml_base_amd64: ARCH=amd64 ## build ml base amd64 image
ml_base_arm64: ARCH=arm64 ## build ml base arm64 image
ml_base_arm64 ml_base_amd64: docker_config
	docker buildx build --load \
		--platform=linux/${ARCH} \
		-t ml_api_base:${GIT_COMMIT}-${ARCH} \
		--build-arg GIT_COMMIT=${GIT_COMMIT} \
		--build-arg GIT_SOURCE=${GIT_SOURCE} \
		-f Dockerfile.base_${ARCH} .
	docker image tag ml_api_base:${GIT_COMMIT}-${ARCH} \
		thespaghettidetective/ml_api_base:${GIT_COMMIT}-${ARCH} 

ml_amd64: ARCH=amd64
ml_arm64: ARCH=arm64
ml_amd64 ml_arm64: ## build ml api arm64 image
	$(MAKE) ml_base_${ARCH}
	docker buildx build --load \
		--platform=linux/${ARCH} \
		-t ml_api:${GIT_COMMIT}-${ARCH} \
		--build-arg GIT_COMMIT=${GIT_COMMIT} \
		--build-arg GIT_SOURCE=${GIT_SOURCE} \
		--build-arg BASE_TAG=${GIT_COMMIT}-${ARCH} \
		-f Dockerfile .

ml: ## build ml api images
	$(MAKE) ml_amd64 ml_arm64

list_images: ## list images if they were built
	@docker image ls | grep ${GIT_COMMIT}

clean: ## delete built images for current commit
	docker image ls | grep ${GIT_COMMIT} | awk '{print $$3}' | sort | uniq | xargs docker rmi -f || true

all: lint-dockerfile ml list_images ## build all

quay_amd64:  ARCH=amd64
quay_arm64:  ARCH=arm64
quay_amd64 quay_arm64:
	$(MAKE) ml_${ARCH}
	docker tag ml_api:${GIT_COMMIT}-${ARCH} quay.io/${QUAY_REPO_USER}/${QUAY_REPO_NAME}:${GIT_COMMIT}-${ARCH}
	docker push quay.io/${QUAY_REPO_USER}/${QUAY_REPO_NAME}:${GIT_COMMIT}-${ARCH}

quay: ## build ml api images and push to quay.io
	$(MAKE) quay_amd64 quay_arm64


bake: ## run image builds with docker buildx, see docker-bake.hcl
	GIT_COMMIT=${GIT_COMMIT} GIT_SOURCE=${GIT_SOURCE} docker buildx bake

.DEFAULT_GOAL := help
.PHONY: help lint-dockerfile ml_base_any ml_base_amd64 ml_base_arm64 ml_any ml_amd64 ml_arm64 ml list_images clean all bake
