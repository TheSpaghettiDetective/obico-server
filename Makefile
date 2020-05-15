.PHONY: build-frontdev build-static vue-live vue-static

build-frontdev:
	docker-compose build --build-arg uid=$(shell id -u) --build-arg gid=$(shell id -g) frontdev

build-static:
	docker-compose run --rm frontdev bash -c "yarn install && yarn build"

vue-live:
	WEBPACK_LOADER_ENABLED=True DEBUG=True docker-compose up

vue-static:
	WEBPACK_LOADER_ENABLED=False docker-compose up
