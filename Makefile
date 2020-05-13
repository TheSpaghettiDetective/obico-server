.PHONY: build-frontdev

build-frontdev:
	docker-compose build --build-arg uid=$(shell id -u) --build-arg gid=$(shell id -g) frontdev
