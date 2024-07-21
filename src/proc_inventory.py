"""
The actual task that performs the inventory of the active project

@author: jldupont
"""
import logging
from typing import List
from pygcloud.models import GCPService   # type: ignore
from pygcloud.gcp.models import Spec     # type: ignore
from pygcloud.gcp.catalog import lookup  # type: ignore
from models import Config, Service
from utils import safe_get_config, get_now_timestamp
from cmds import get_inventory
from store import store_spec_list, store_config


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

    info(f"> Configuration from : {path}")
    config: Config = safe_get_config(path)

    bucket = config.TargetBucket
    bucket_project = config.TargetBucketProject

    project = config.ProjectId
    services = config.Services
    regions = config.Regions

    info(f"> Inventoring project: {config.ProjectId}")
    info(f"> Bucket: gs://{bucket} in project '{bucket_project}'")

    ts = get_now_timestamp()
    info(f"> Using the following timestamp: {ts}")

    service: Service
    for service_class_name, service in services.items():

        if not service.enabled:
            info(f"! Skipping disabled {service_class_name}")
            continue

        service_class: GCPService = lookup(service_class_name)
        if not service_class:
            error(f"Service class '{service_class_name}' "
                  "not found... skipping")
            continue

        requires_location = service_class.LISTING_REQUIRES_LOCATION

        specs: List[Spec] = []

        if requires_location:
            specs = list_with_locations(project, service_class, regions)
        else:
            specs = list_no_location(project, service_class)

        try:
            store_spec_list(config, ts, service_class_name, specs)
        except Exception as e:
            error(f"! Failed to store spec list: {e}")
            print(specs)

    try:
        store_config(config, ts)
    except Exception as e:
        error(f"! Failed to store config: {e}")
        info(f"> Objects related to the timestamp({ts}) will be dangling")

    info("> Done")
