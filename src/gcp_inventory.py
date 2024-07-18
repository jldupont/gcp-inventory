#!/usr/bin/env python3
"""
@author: jldupont
"""
import logger
import logging
from pygcloud.models import Result
from models import Config
from utils import safe_get_config, abort
from cmds import check_if_bucket_exists, check_if_service_account_exists, \
    check_if_cloud_run_job_exists, deploy_cloud_run_job

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

        info(f"> Configuration from : {path}")
        config: Config = safe_get_config(path)

        info(f"> Deploying to project: {config.ProjectId}")

        info(f"* Checking if bucket '{config.TargetBucket}' exists")
        if not check_if_bucket_exists(config):
            abort("The bucket does not exist. Please create it first")

        info(f"  Bucket '{config.TargetBucket}' exists")

        if config.ServiceAccountEmail is not None:
            info("* Checking if service account"
                 f" '{config.ServiceAccountEmail}' exists")
            if not check_if_service_account_exists(config):
                abort("The service account does not exist. "
                      "Please create it first")
            info(f"  Service account '{config.ServiceAccountEmail}' exists")

        info("* Checking if Cloud Run Job 'gcp-inventory' exists")
        exists_already = check_if_cloud_run_job_exists(config)
        if exists_already:
            info("  Cloud Run Job 'gcp-inventory' exists")
            action = "Updating"
        else:
            action = "Creating"
            info("  Cloud Run Job 'gcp-inventory' does not exist"
                 f" in region: {config.JobRegion}")

        info(f"> {action} Cloud Run Job... ")
        result: Result = deploy_cloud_run_job(config, exists_already)
        info(f"> Result: {result.success}")


if __name__ == "__main__":
    import fire
    fire.Fire(Commands)
