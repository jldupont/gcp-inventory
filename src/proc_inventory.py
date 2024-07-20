"""
The actual task that performs the inventory of the active project

@author: jldupont
"""
import logging
from typing import List
from pygcloud.models import GCPService
from pygcloud.gcp.models import Spec
from models import Config
from utils import safe_get_config
from pygcloud.gcp.catalog import lookup
from cmds import get_inventory


info = logging.info
error = logging.error


def get_listings(project: str,
                 service: GCPService,
                 region: str) -> List[Spec]:

    info(f"* Retrieving {service.__name__} instance(s) "
         f"from region({region or 'all'}) ...")
    specs: List[Spec] = get_inventory(project, service, region)
    return specs


def list_with_locations(project: str,
                        service: GCPService,
                        regions: List[str]) -> List[Spec]:

    all_entries: List[Spec] = []
    region: str

    for region in regions:
        entries = get_listings(project, service, region)
        all_entries.extend(entries)

    return all_entries


def list_no_location(project: str,
                     service: GCPService) -> List[Spec]:
    return get_listings(project, service, None)


def run(path: str = 'config.yaml'):
    #
    # Configuration
    #
    info(f"> Configuration from : {path}")
    config: Config = safe_get_config(path)

    bucket = config.TargetBucket
    bucket_project = config.TargetBucketProject

    project = config.ProjectId
    services = config.Services
    regions = config.Regions

    info(f"> Inventoring project: {config.ProjectId}")
    info(f"> Bucket: gs://{bucket} in project '{bucket_project}'")

    for service_class_name in services:

        service_class: GCPService = lookup(service_class_name)
        if not service_class:
            error(f"Service class '{service_class_name}' "
                  "not found... skipping")
            continue

        requires_location = service_class.LISTING_REQUIRES_LOCATION

        result: List[Spec] = []

        if requires_location:
            result = list_with_locations(project, service_class, regions)
        else:
            result = list_no_location(project, service_class)

        print(result)
        print("\n")
