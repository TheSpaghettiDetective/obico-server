help:
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

lint-dockerfile: ## Runs hadolint against application dockerfile
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint backend/Dockerfile.base
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint backend/Dockerfile
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint ml_api/Dockerfile.base_amd64
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint ml_api/Dockerfile.base_arm64
	docker run --rm -v "$(PWD):/data" -w "/data" hadolint/hadolint hadolint ml_api/Dockerfile

ml_api: ## build ml_api images
	$(MAKE) -C ml_api all

backend: ## build backend images
	$(MAKE) -C backend all

ml: docker_config ml_amd64 ml_arm64

all: lint-dockerfile ml

.DEFAULT_GOAL := help
.PHONY: help lint-dockerfile ml_api backend all


