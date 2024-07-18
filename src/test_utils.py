"""
@author: jldupont
"""
import pytest
import os
from models import Config, Service
from utils import get_config_from_string, parse_config


@pytest.fixture
def sample_config():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    tpl_dir = os.path.abspath(os.path.join(this_dir, "../templates"))
    path_to_sample_config = os.path.join(tpl_dir, "all.yaml")

    with open(path_to_sample_config, "r") as f:
        return f.read()


def test_get_config_from_string(sample_config):
    result = get_config_from_string(sample_config)
    assert isinstance(result, dict)


def test_parse_config(sample_config):
    result: dict = get_config_from_string(sample_config)
    config: Config = parse_config(result)

    assert config.ProjectId == "PROJECT_NOT_SET"
    assert isinstance(config.Regions, list)
    assert len(config.Regions) == 2
    assert isinstance(config.Services, dict)
    assert isinstance(config.Services["BackendService"], Service)

    s = config.Services["BackendService"]
    assert s.enabled is True


def test_invalid_config():
    with pytest.raises(ValueError):
        services = {"BackendService": {"enabled": True, "extra": 666}}

        Config(Services=services, JobRegion="")

    with pytest.raises(ValueError):
        Config(Services={}, Regions=None, JobRegion="")
