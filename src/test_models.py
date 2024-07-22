"""
@author: jldupont
"""
import pytest
from pygcloud.models import OptionalParam
from models import Config


@pytest.fixture
def config():
    return Config(Schedule="* * * * *", JobRegion="jobregion")


def test_config(config):
    assert config.ServiceAccountEmail is None, \
        print(config.ServiceAccountEmail)


def test_config_to_json(config):
    import dataclasses
    import json
    dic = dataclasses.asdict(config)
    json_str = json.dumps(dic, indent=4)
    js = json.loads(json_str)
    assert js["JobRegion"] == "jobregion", print(js)


def test_optional_param(config):

    osa = OptionalParam("--sa", config.ServiceAccountEmail)
    osc = OptionalParam("--sc", config.Schedule)

    assert osa == []
    assert osc == ["--sc", config.Schedule]
