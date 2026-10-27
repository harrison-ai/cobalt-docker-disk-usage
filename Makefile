.DEFAULT_GOAL := help
IMAGE_NAME := ghcr.io/harrison-ai/cobalt-disk-usage

## build:                       build the docker image
build:
	./scripts/build.sh $(IMAGE_NAME)

## publish:                     push the docker image to registry with the given TAG
publish:
	@test -n "${TAG}" || ( echo "TAG environment variable must be set" && return 1 )
	./scripts/publish.sh $(IMAGE_NAME) ${TAG}

## sync:                        install dependencies into the local virtual environment
sync:
	uv sync

## requirements:                generate requirements.txt from pyproject.toml
requirements:
	uv export --format requirements.txt --no-hashes --no-dev --no-emit-project -o requirements.txt

## help:                        show this help
help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)
