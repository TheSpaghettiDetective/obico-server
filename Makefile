.PHONY: build-frontdev vue-demo

build-frontdev:
	docker-compose -f docker-compose.yml -f docker-compose.override.vue-demo.yml build --build-arg uid=$(shell id -u) --build-arg gid=$(shell id -g) frontdev

vue-demo: build-frontdev
	docker-compose -f docker-compose.yml -f docker-compose.override.vue-demo.yml up

build-static:
	docker-compose -f docker-compose.yml -f docker-compose.override.vue-demo.yml run --rm frontdev yarn build
