"""
@author: jldupont
"""
import logging
from pygcloud.models import Result
from pygcloud.gcp.models import ProjectDescription
from pygcloud.cmds import cmd_retrieve_project_description
from models import Config
from utils import safe_get_config, abort
from cmds import check_if_bucket_exists, check_if_service_account_exists, \
    check_if_cloud_run_job_exists, deploy_cloud_run_job, \
    check_if_cloud_run_job_scheduler_exists, deploy_cloud_run_scheduler

info = logging.info


def run(path: str = 'config.yaml'):

    info(f"> Configuration from : {path}")
    config: Config = safe_get_config(path)

    info(f"> Deploying to project: {config.ProjectId}")

    info("* Retrieving project description")
    project_description: ProjectDescription = \
        cmd_retrieve_project_description(config.ProjectId)

    info(f"  Project number: {project_description.projectNumber}")
    config.ProjectNumber = project_description.projectNumber

    info(f"* Checking if bucket '{config.TargetBucket}' exists")
    if not check_if_bucket_exists(config):
        abort("The bucket does not exist. Please create it first")

    info(f"  Bucket '{config.TargetBucket}' in project "
         f"'{config.TargetBucketProject}' exists")

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
    if not result.success:
        abort(f"Failed to {action} Cloud Run Job")

    info("> Checking if execution schedule is installed ...")
    exists_already = check_if_cloud_run_job_scheduler_exists(config)
    if exists_already:
        info("  Cloud Scheduler exists")
        action = "Updating"
    else:
        action = "Creating"
        info("  Cloud Scheduler does not exist")

    info(f"> {action} Cloud Scheduler... ")
    result: Result = deploy_cloud_run_scheduler(config, exists_already)
    if not result.success:
        abort(f"Failed to {action} Cloud Scheduler")

    info("! Done")
