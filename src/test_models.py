"""
@author: jldupont
"""
import pytest
from models import Config, OptionalParam


@pytest.fixture
def config():
    return Config(Services={}, Schedule="* * * * *", JobRegion="jobregion")


def test_config(config):
    assert config.ServiceAccountEmail is None, \
        print(config.ServiceAccountEmail)


def test_optional_param(config):

    osa = OptionalParam("--sa", config.ServiceAccountEmail)
    osc = OptionalParam("--sc", config.Schedule)

    assert osa == []
    assert osc == ["--sc", config.Schedule]
