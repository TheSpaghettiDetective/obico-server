.PHONY: build-frontdev build-static vue-live vue-static

build-frontdev:
	docker-compose -f docker-compose.yml -f docker-compose.override.vue-demo.yml build --build-arg uid=$(shell id -u) --build-arg gid=$(shell id -g) frontdev

build-static:
	docker-compose -f docker-compose.yml -f docker-compose.override.vue-demo.yml run --rm frontdev yarn build

vue-live:
	WEBPACK_LOADER_ENABLED=True docker-compose -f docker-compose.yml -f docker-compose.override.vue-demo.yml up

vue-static:
	WEBPACK_LOADER_ENABLED=False docker-compose -f docker-compose.yml -f docker-compose.override.vue-demo.yml up
