"""
https://cloud.google.com/storage/docs/uploading-objects

gcloud storage cp OBJECT_LOCATION gs://DESTINATION_BUCKET_NAME

@author: jldupont
"""
import logging
from typing import List
from tempfile import mkdtemp
from pygcloud.gcp.models import Spec
from models import Config
from utils import spec_list_to_json

info = logging.info

TEMPDIR = mkdtemp()


def store_spec_list(config: Config,
                    ts: str,
                    service_class_name: str,
                    specs: List[Spec]):
    """
    gs://bucket/{SERVICE_CLASS}/{TIMESTAMP}_inventory.json
    """
    path = f"{TEMPDIR}/{service_class_name}_{ts}_inventory.json"
    liste: str = spec_list_to_json(specs)

    info(f"> Writing inventory to temporary file: {path}")

    with open(path, 'w') as f:
        f.write(liste)


def store_config(config: Config, ts: str):
    """
    gs://bucket/{TIMESTAMP}_config.json
    """
    path = f"{TEMPDIR}/{ts}_config.json"
    obj_str: str = config.to_json()

    info(f"> Writing config to temporary file: {path}")

    with open(path, 'w') as f:
        f.write(obj_str)
