CUR_UID = $(shell id -u)
CUR_GID = $(shell id -g)

.PHONY: env

env:
	printf '%s\n%s\n' "UID=${CUR_UID}" "GID=${CUR_GID}" > .env
