#!/bin/bash
if [ ! -f ./config.yaml ]; then
    echo "Copying default template to 'config.yaml'"
    echo "Modify this file to customize the inventory"
    @cp templates/config.yaml ./config.yaml
else
    echo "Using existing config.yaml"
fi
