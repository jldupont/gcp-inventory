#
# @author: jldupont
#
RELEASE=0.0.2

SHELL := /bin/bash
RED=\033[1;31m
GREEN=\033[1;32m
NC=\033[0m

install: requirements.txt
	@echo "Installing requirements"
	@echo -e "${GREEN}NOTE:${NC} make sure you have Google Cloud SDK installed with 'gcloud'"
	@pip install -r requirements.txt 1> /dev/null
	
	# TODO check compatibility of existing config.yaml file & describe the changes

	@./maybe_prepare_config.sh

test:
	@pytest -v src/

deploy:
	@echo "Starting deployment of the Cloud Run Job (creation or update)"
	@src/gcp_inventory.py deploy

help:
	@src/gcp_inventory.py --help

commit:
	@git add .
	@git commit -m "step"
	@git push

release:
	@git add .
	@git commit -m "release ${RELEASE}"
	@git push
	@git tag "v${RELEASE}" HEAD
	@git tag latest HEAD
	@git push --tags

push:
	@git push