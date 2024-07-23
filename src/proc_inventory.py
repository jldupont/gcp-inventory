"""
The actual task that performs the inventory of the active project

@author: jldupont
"""
import logging
from typing import List, Union
from pygcloud.models import GCPService   # type: ignore
from pygcloud.gcp.models import Spec, ServiceDescription  # type: ignore
from pygcloud.gcp.catalog import \
    get_service_classes_from_services_list  # type: ignore
from pygcloud.cmds import cmd_retrieve_enabled_services   # type: ignore
from models import Config, Snapshot
from utils import get_config_from_environment, get_now_timestamp, abort
from cmds import get_inventory, upload_path_recursive
from store import store_spec_list, store_config, get_temp_dir, store_snapshot


debug = logging.debug
info = logging.info
error = logging.error


def get_listings(project: str,
                 service: GCPService,
                 location: Union[str, None] = None) -> List[Spec]:

    info(f"* Retrieving {service.__name__} instance(s) "
         f"from location({location or 'all'}) ...")
    specs: List[Spec] = get_inventory(project, service, location)
    return specs


def list_with_locations(project: str,
                        service: GCPService,
                        locations: str) -> List[Spec]:

    all_entries: List[Spec] = []

    location_list: List[str] = locations.split(";")
    location: str

    for location in location_list:
        entries = get_listings(project, service, location)
        all_entries.extend(entries)

    return all_entries


def list_no_location(project: str,
                     service: GCPService) -> List[Spec]:
    return get_listings(project, service, None)


def run(path: str = 'config.yaml'):

    config: Config = get_config_from_environment()
    info(f"> Configuration: {config}")

    project: str = config.TargetProjectId

    liste: List[ServiceDescription] = \
        cmd_retrieve_enabled_services(project)

    debug(f"> List of services enabled: {liste}")

    services: List[GCPService] = \
        get_service_classes_from_services_list(liste)

    info(f"> List of supported services in the project: {services}")

    bucket = config.TargetBucket
    bucket_project = config.TargetBucketProject
    locations: str = config.TargetLocations

    info(f"> Inventoring project: {config.TargetProjectId}")
    info(f"> Bucket: gs://{bucket} in project '{bucket_project}'")

    ts = get_now_timestamp()
    info(f"> Using the following timestamp: {ts}")

    processed_service_classes: List[str] = []

    for service_class in services:

        service_class_name = service_class.__name__

        requires_location = service_class.LISTING_REQUIRES_LOCATION

        specs: List[Spec] = []

        if requires_location:
            specs = list_with_locations(project, service_class, locations)
        else:
            specs = list_no_location(project, service_class)

        try:
            store_spec_list(config, ts, service_class_name, specs)
        except Exception as e:
            error(f"! Failed to store spec list: {e}")
            continue

        processed_service_classes.append(service_class_name)
        info(f"> Done with {service_class_name}")

    try:
        store_config(config, ts)
        info("> Done with config")
    except Exception as e:
        abort(f"! Failed to store config: {e}")

    snapshot: Snapshot = \
        Snapshot(Timestamp=ts, ServiceClasses=processed_service_classes)

    try:
        store_snapshot(config, snapshot)
        info("> Done with snapshot 'latest'")
    except Exception as e:
        abort(f"! Unable to create snapshot 'latest': {e}")

    info(f"> Uploading files to bucket: gs//{config.TargetBucket}")

    tempdir = get_temp_dir()
    result = upload_path_recursive(config.TargetBucketProject,
                                   config.TargetBucket,
                                   f"{tempdir}/{config.TargetProjectId}")

    if not result.success:
        abort(f"! Failed to upload files to bucket: {result.message}")

    info("> Done")
