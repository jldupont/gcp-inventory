#
# @author: jldupont
#
RED=\033[1;31m
GREEN=\033[1;32m
NC=\033[0m

install: requirements.txt
	@echo "Installing requirements"
	@echo -e "${GREEN}NOTE:${NC} make sure you have Google Cloud SDK installed with 'gcloud'"
	@pip install -r requirements.txt 1> /dev/null
	

	@echo "Copying default template to 'config.yaml'"
	@echo "Modify this file to customize the inventory"
	@cp templates/all.yaml ./config.yaml
	
test:
	@pytest -v src/

deploy:
	@echo "Starting deployment of the Cloud Run Job... (if applicable)"
	@echo ${@:2}
	@src/gcp_inventory.py deploy ${@:2}
	# Ensure GCS bucket exists, create if not
	# Ensure Service Account for Cloud Run Job exists
	# Ensure config file exists and is valid

help:
	@src/gcp_inventory.py --help
