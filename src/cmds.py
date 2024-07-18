"""
@author: jldupont
"""
from pygcloud.core import GCloud
from pygcloud.models import Result
from models import Config, OptionalParam


def get_cmd_storage_bucket_describe(config: Config, bucket: str) -> GCloud:
    return GCloud("storage", "buckets", "describe", f"gs://{bucket}",
                  "--project", config.ProjectId,
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
                  "--source", ".",
                  "--schedule", config.Schedule,
                  OptionalParam("--service-account",
                                config.ServiceAccountEmail),
                  cmd="gcloud",
                  exit_on_error=False,
                  log_error=False)


def deploy_cloud_run_job(config: Config, already_exists: bool) -> Result:

    cmd = get_cmd_cloud_run_job_create_or_update(config, already_exists)
    result: Result = cmd()
    return result

