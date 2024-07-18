"""
@author: jldupont
"""
from pygcloud.core import GCloud
from pygcloud.models import Result
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
