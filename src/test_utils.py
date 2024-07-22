"""
@author: jldupont
"""
import pytest
import os
from models import Config
from utils import get_config_from_string, parse_config, \
    get_config_from_environment


@pytest.fixture
def sample_config():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    tpl_dir = os.path.abspath(os.path.join(this_dir, "../templates"))
    path_to_sample_config = os.path.join(tpl_dir, "config.yaml")

    with open(path_to_sample_config, "r") as f:
        return f.read()


def test_get_config_from_string(sample_config):
    result = get_config_from_string(sample_config)
    assert isinstance(result, dict)


def test_parse_config(sample_config):
    result: dict = get_config_from_string(sample_config)
    config: Config = parse_config(result)

    assert config.ProjectId == "PROJECT_NOT_SET"
    assert isinstance(config.TargetLocations, str)
    assert len(config.TargetLocations.split(",")) == 2


def test_config_from_environment():

    os.environ['SCHEDULE'] = "0 */1 * * *"

    c = get_config_from_environment()
    assert c.Schedule == "0 */1 * * *"
