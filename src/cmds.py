"""
@author: jldupont
"""
from pygcloud.core import GCloud
from pygcloud.models import Result, OptionalParam
from models import Config


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
                  "--image", "docker.io/jldupont/gcp-inventory:main",
                  OptionalParam("--service-account",
                                config.ServiceAccountEmail),
                  cmd="gcloud",
                  exit_on_error=False,
                  log_error=False)


def deploy_cloud_run_job(config: Config, already_exists: bool) -> Result:

    cmd = get_cmd_cloud_run_job_create_or_update(config, already_exists)
    result: Result = cmd()
    return result


def get_cmd_scheduler_for_cloud_run_job_describe(config: Config) -> GCloud:
    return GCloud("scheduler", "jobs", "describe", "gcp-inventory",
                  "--project", config.ProjectId,
                  "--location", config.JobRegion,
                  "--format", "json"
                  cmd="gcloud",
                  exit_on_error=False)


def check_if_cloud_run_job_scheduler_exists(config: Config) -> bool:
    cmd = get_cmd_scheduler_for_cloud_run_job_describe(config)
    result: Result = cmd()
    return result.success

'''
gcloud scheduler jobs create http SCHEDULER_JOB_NAME \
  --location SCHEDULER_REGION \
  --schedule="SCHEDULE" \
  --uri="https://CLOUD_RUN_REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT-ID/jobs/JOB-NAME:run" \
  --http-method POST \
  --oauth-service-account-email PROJECT-NUMBER-compute@developer.gserviceaccount.com
'''

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
