.PHONY: build-web-base-1.1 build-images build-static frontdev-up vue-live vue-static

BASENAME = $(shell basename $(shell pwd) | tr '[:upper:]' '[:lower:]')

build-web-base-1.1:
	docker build -t thespaghettidetective/web:base-1.1 -f web/Dockerfile.base web

build-images:
	docker-compose build --build-arg with_node=1 --build-arg user=user --build-arg group=user --build-arg uid=$(shell id -u) --build-arg gid=$(shell id -g)

build-web-and-tasks:
	docker-compose build --build-arg with_node=1 --build-arg user=user --build-arg group=user --build-arg uid=$(shell id -u) --build-arg gid=$(shell id -g) web tasks

build-static:
	docker-compose run --rm --name $(BASENAME)_frontbuilder --no-deps                    web bash -c "cd frontend && yarn install && yarn build"

frontdev-up:
	docker-compose run --rm --name $(BASENAME)_frontdev --no-deps -p 127.0.0.1:7070:7070 web bash -c "cd frontend && yarn install && yarn serve"

vue-live:
	WEBPACK_LOADER_ENABLED=True DEBUG=True docker-compose up

vue-static:
	WEBPACK_LOADER_ENABLED=False docker-compose up
