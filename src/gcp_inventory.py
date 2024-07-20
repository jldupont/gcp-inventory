#!/usr/bin/env python3
"""
@author: jldupont
"""
import logger
import logging
from proc_deploy import run as run_deploy
from proc_inventory import run as run_inventory

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
        run_deploy(path)

    def inventory(self, path: str = 'config.yaml', loglevel: str = 'INFO'):
        """
        Performs the inventory in the active project

        --path: path to configuration file
        --loglevel: loglevel to use (DEBUG, INFO, WARNING, ERROR)
        """
        logger.set_params(loglevel)
        run_inventory(path)


if __name__ == "__main__":
    import fire
    fire.Fire(Commands)
