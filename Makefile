.PHONY: build-web-base-1.2 build-images build-static frontdev-up vue-live vue-static

build-web-base-1.2:
	docker build -t thespaghettidetective/web:base-1.2 -f web/Dockerfile.base web

build-images:
	docker-compose build --build-arg user=user --build-arg group=user --build-arg uid=$(shell id -u) --build-arg gid=$(shell id -g)

build-static:
	docker-compose run --rm --name frontbuilder --no-deps                    web bash -c "cd frontend && yarn install && yarn build"

frontdev-up:
	docker-compose run --rm --name frontdev --no-deps -p 127.0.0.1:7070:7070 web bash -c "cd frontend && yarn install && yarn serve"

vue-live:
	WEBPACK_LOADER_ENABLED=True DEBUG=True docker-compose up

vue-static:
	WEBPACK_LOADER_ENABLED=False docker-compose up
