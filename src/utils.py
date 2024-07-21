"""
@author: jldupont
"""
import os
import sys
import yaml
import logging
from typing import List
from models import Config
from pygcloud.gcp.models import Spec  # type: ignore
from pygcloud.utils import FlexJSONEncoder  # type: ignore


info = logging.info

error = logging.error


def abort(msg):
    error(msg)
    sys.exit(1)


try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

PROJECT_ID = os.environ.get("_PROJECT_ID", False) or \
             os.environ.get("PROJECT_ID", False) or \
             os.environ.get("PROJECT", False)


def get_config(path: str = None, yaml_string: str = None) -> Config:
    """
    The config should normally be located in ./config.yaml
    """
    if isinstance(yaml_string, str):
        raw_config = get_config_from_string(yaml_string)
    else:
        raw_config = get_config_from_file(path)

    project_id_from_config_file = raw_config.get("ProjectId", None)

    project_id = PROJECT_ID if PROJECT_ID is not False \
        else project_id_from_config_file

    raw_config["ProjectId"] = project_id

    return Config(**raw_config)


def get_config_from_path(path: str = 'config.yaml') -> dict:

    return get_config_from_file(path)


def get_config_from_file(path: str = 'config.yaml') -> dict:

    assert isinstance(path, str), print(f"Invalid path: {path}")

    with open(path, 'r') as stream:
        try:
            result = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise ValueError(f"Error parsing config file: {exc}")

    return result


def get_config_from_string(yaml_str: str) -> dict:

    try:
        result = yaml.load(yaml_str, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"Error parsing config data: {exc}")

    return result


def parse_config(config_data: dict) -> Config:
    return Config(**config_data)


def safe_get_config(path: str) -> Config:

    try:
        config: Config = get_config(path=path)
    except Exception as e:
        error(f"Error attempting to get configuration: {e}")
        sys.exit(1)
    return config


def get_now_timestamp():
    from datetime import datetime, timezone

    utc_now = datetime.now(timezone.utc)
    formatted_datetime = utc_now.strftime("%Y-%m-%d-%H-%M-%S")

    return formatted_datetime


def spec_list_to_json(spec_list: List[Spec]) -> str:
    import json
    dics = [spec.to_dict() for spec in spec_list]
    return json.dumps(dics, cls=FlexJSONEncoder)
