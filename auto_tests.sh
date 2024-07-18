#!/bin/bash

export PYTEST_ADDOPTS="--color=yes"
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

watch --color -n 2 pytest
