"""
https://cloud.google.com/storage/docs/uploading-objects

gcloud storage cp OBJECT_LOCATION gs://DESTINATION_BUCKET_NAME

@author: jldupont
"""
import logging
from typing import List
from tempfile import mkdtemp
from pygcloud.tools import mkdir
from pygcloud.gcp.models import Spec
from models import Config
from utils import spec_list_to_json


error = logging.error
info = logging.info

TEMPDIR = mkdtemp()


def get_temp_dir():
    global TEMPDIR
    return TEMPDIR


def store_spec_list(config: Config,
                    ts: str,
                    service_class_name: str,
                    specs: List[Spec]):
    """
    gs://bucket/{SERVICE_CLASS}/{TIMESTAMP}_inventory.json
    """
    base_path = f"{config.ProjectId}/{service_class_name}"
    path = f"{TEMPDIR}/{base_path}/{ts}_inventory.json"
    liste: str = spec_list_to_json(specs)

    mkdir(f"{TEMPDIR}/{base_path}")

    info(f"> Writing inventory to temporary file: {path}")

    with open(path, 'w') as f:
        f.write(liste)


def store_config(config: Config, ts: str):
    """
    gs://bucket/{TIMESTAMP}_config.json
    """
    base_path = f"{config.ProjectId}"
    path = f"{TEMPDIR}/{base_path}/{ts}_config.json"
    obj_str: str = config.to_json()

    mkdir(f"{TEMPDIR}/{base_path}")

    info(f"> Writing config to temporary file: {path}")

    with open(path, 'w') as f:
        f.write(obj_str)
