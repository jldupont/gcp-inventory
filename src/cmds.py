"""
@author: jldupont
"""
import logging
from typing import List, Union
from pygcloud.core import GCloud  # type: ignore
from pygcloud.models import Result, OptionalParam, GCPService  # type: ignore
from pygcloud.gcp.models import Spec  # type: ignore
from models import Config


error = logging.error
info = logging.info


def get_inventory(project: str,
                  service_class: GCPService,
                  location: Union[str, None] = None,
                  exit_on_error: bool = False
                  ) -> List[Spec]:

    cmd = get_cmd_list(project, service_class, location, exit_on_error)
    result: Result = cmd()

    #
    # I am choosing to log errors here instead of deferring to the caller:
    # this keeps the caller's code cleaner but I might revisit this later
    #
    if not result.success:
        if "INVALID_ARGUMENT: Location" in result.message:
            info(f"! {service_class.__name__} does appear "
                 f"to be available in location: {location}")
            return []

        error(f"Failed to list {service_class.__name__}: {result.message}")
        return []

    spec_class: Spec = service_class.SPEC_CLASS  # type: ignore

    try:
        specs: List[Spec] = spec_class.from_json_list(result.message)
    except Exception as e:
        error("! Failed to parse entries related to "
              f"{service_class.__name__}: {e}")
        return []

    return specs


def get_cmd_list(project: str,
                 service_class: GCPService,
                 location: Union[str, None] = None,
                 exit_on_error: bool = False
                 ) -> GCloud:

    group = service_class.GROUP
    group.extend(service_class.GROUP_SUB_DESCRIBE)

    where = "--region"

    if location is not None:
        if service_class.LISTING_REQUIRES_LOCATION:
            where = "--location"

    return GCloud(group, "list",
                  "--project", project,
                  OptionalParam(where, location),
                  "--format", "json",
                  cmd="gcloud",
                  exit_on_error=exit_on_error)


def get_cmd_storage_bucket_describe(config: Config, bucket: str) -> GCloud:
    return GCloud("storage", "buckets", "describe", f"gs://{bucket}",
                  "--project", config.TargetBucketProject,
                  "--format", "json",
                  cmd="gcloud",
                  exit_on_error=False,
                  log_error=False)


def check_if_bucket_exists(config: Config) -> bool:
    bucket = config.TargetBucket
    cmd = get_cmd_storage_bucket_describe(config, bucket)
    result: Result = cmd()
    return result.success


def get_cmd_iam_service_account_describe(config: Config) -> GCloud:
    return GCloud("iam", "service-accounts", "describe",
                  config.ServiceAccountEmail,
                  "--project", config.ProjectId,
                  cmd="gcloud",
                  exit_on_error=False,
                  log_error=False)


def check_if_service_account_exists(config: Config) -> bool:
    sa_email = config.ServiceAccountEmail
    assert isinstance(sa_email, str), print("Service account cannot be None")

    cmd = get_cmd_iam_service_account_describe(config)
    result: Result = cmd()
    return result.success


def get_cmd_cloud_run_job_describe(config: Config) -> GCloud:
    return GCloud("run", "jobs", "describe", "gcp-inventory",
                  "--project", config.ProjectId,
                  "--region", config.JobRegion,
                  cmd="gcloud",
                  exit_on_error=False,
                  log_error=False)


def check_if_cloud_run_job_exists(config: Config) -> bool:
    cmd = get_cmd_cloud_run_job_describe(config)
    result: Result = cmd()
    return result.success


def get_cmd_cloud_run_job_create_or_update(config: Config,
                                           exists_already: bool) -> GCloud:
    """
    https://cloud.google.com/sdk/gcloud/reference/run/jobs/create
    """
    action = "create" if not exists_already else "update"

    return GCloud("run", "jobs", action, "gcp-inventory",
                  "--project", config.ProjectId,
                  "--region", config.JobRegion,
                  "--image",
                  "docker.io/jldupont/gcp-inventory"
                  f":{config.ContainerRelease}",
                  "--set-env-vars",
                  f"TARGETPROJECTID={config.TargetProjectId},"
                  f"TARGETLOCATIONS={config.TargetLocations},"
                  f"TARGETBUCKET={config.TargetBucket},"
                  f"TARGETBUCKETPROJECT={config.TargetBucketProject}",
                  OptionalParam("--service-account",
                                config.ServiceAccountEmail),
                  cmd="gcloud",
                  exit_on_error=False,
                  log_error=True)


def deploy_cloud_run_job(config: Config, already_exists: bool) -> Result:

    cmd = get_cmd_cloud_run_job_create_or_update(config, already_exists)
    result: Result = cmd()
    return result


def get_cmd_scheduler_for_cloud_run_job_describe(config: Config) -> GCloud:
    return GCloud("scheduler", "jobs", "describe", "gcp-inventory",
                  "--project", config.ProjectId,
                  "--location", config.JobRegion,
                  "--format", "json",
                  cmd="gcloud",
                  exit_on_error=False)


def check_if_cloud_run_job_scheduler_exists(config: Config) -> bool:
    cmd = get_cmd_scheduler_for_cloud_run_job_describe(config)
    result: Result = cmd()
    return result.success


def get_cmd_cloud_run_job_scheduler_create_or_update(config: Config,
                                                     exists_already: bool) \
                                                     -> GCloud:
    """
    https://cloud.google.com/sdk/gcloud/reference/run/jobs/create
    """
    action = "create" if not exists_already else "update"
    region = config.JobRegion

    uri = f"https://{region}-run.googleapis.com/apis/run.googleapis.com/v1/" \
          + f"namespaces/{config.ProjectId}/jobs/gcp-inventory:run"

    sa_email = f"{config.ProjectNumber}-compute@developer.gserviceaccount.com"

    return GCloud("scheduler", "jobs", action, "http", "gcp-inventory",
                  "--location", region,
                  "--schedule", config.Schedule,
                  "--uri", uri,
                  "--http-method", "POST",
                  "--oauth-service-account-email", sa_email,
                  "--project", config.ProjectId,
                  cmd="gcloud",
                  exit_on_error=False,
                  log_error=False)


def deploy_cloud_run_scheduler(config: Config, exists_already: bool) -> Result:

    cmd = get_cmd_cloud_run_job_scheduler_create_or_update(config,
                                                           exists_already)
    result: Result = cmd()
    return result


def upload_path_recursive(target_project: str,
                          target_bucket: str,
                          file_path: str):
    """
    Upload a local file to a specific GCS bucket object path
    """
    cmd = GCloud("storage", "cp", file_path,
                 f"gs://{target_bucket}",
                 "--project", target_project,
                 "--recursive",
                 "--format", "json",
                 cmd="gcloud",
                 exit_on_error=False)
    result: Result = cmd()
    return result
