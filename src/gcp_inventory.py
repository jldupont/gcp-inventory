#!/usr/bin/env python3
"""
@author: jldupont
"""
import logger
import logging
from models import Config
from utils import safe_get_config, abort
from cmds import check_if_bucket_exists

info = logging.info


class Commands:
    """
    Gathering inventory information and uploading to GCS

    The following commands are available:
    * deploy: Deploy the Cloud Run Job that will inventory the target project
    """

    def deploy(self,
               path: str = 'config.yaml',
               loglevel: str = 'INFO',
               ):
        """
        Deploy the Cloud Run Job that will inventory the target project

        --path: path to configuration file
        --loglevel: loglevel to use (DEBUG, INFO, WARNING, ERROR)
        """
        logger.set_params(loglevel)

        info(f"> Deploying to path: {path}")
        config: Config = safe_get_config(path)

        info(f"> Deploying to project: {config.ProjectId}")
        info(f"* Checking if bucket '{config.TargetBucket}' exists")
        if not check_if_bucket_exists(config):
            abort("The bucket does not exist. Please create it first")

        info(f"  Bucket '{config.TargetBucket}' exists")


if __name__ == "__main__":
    import fire
    fire.Fire(Commands)
