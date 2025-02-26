# gcp-inventory

This project is about exporting an inventory of descriptions related to service instances & resources from a GCP project.

The inventory can be used in different ways, e.g.:

* Draw a diagram representing relationships between entities
* Perform policy related processes

# Security & Privacy

The standard setup is totally under the control of the user.
There is a capability to filter-out information to any granularity deemed required.

# Non-goals

    1. This tool is not meant to perform near/real-time infrastructure/services policying.
    2. The inventory process runs asynchronously from other processes that might change the inventory. No attempt is made to synchronise across such processes.

# Use-cases

1. Single project
1. Multiple projects (unrelated to one another)
1. Multiple projects part of a single workload

# Deployment options

1. Inside the target project
1. Outside the target project(s)

# Some challenges

1. Balancing configuration complexity and service catalog evolution

The catalog of supported services both on GCP and this project will expand over time. Considering most projects will only consume a subset of service classes, the challenge is devise sensible defaults for the configuration.

* On one hand, enabling by default all supported service classes will lead to ever increasing inventory execution time
* On the other hand, requiring explicitly configuring the target service classes goes against the essence of automation
* There is of course the option to explicitly disable specific service classes.
* And finally there is the option to "auto-detect" service classes that are currently used. This is the option I decided to leverage.

2. Listing some services requires specifying a location

It is currently not possible to list the locations being used in a project at the moment.

Considering the ever growing list of locations and the time it takes to list on a per service/location basis, it is more desirable to specify the location(s) in scope through configuration.

# Usage

## Planning

Usually, an SDLC process for governing application lifecycle is leveraged. In this context, it is best practice to have multiple environments (aka `projects`) in a `workload` (i.e. collection of projects).

From the above, it is reasonable one would want to use `gcp-inventory` on all projects in the workload. Thus, the following steps are assumed:

* Choose a project where the target GCS bucket will provisioned (e.g. the '-src' project along with source code)
* Further to the previous point, consider using a separate project if you plan to expose the bucket to a third party. This step is not strictly required: it really depends on your risk appetite. Properly securing a GCS bucket is fairly straightforward now.
* Consider using [lifecycle management](https://cloud.google.com/storage/docs/lifecycle) on the bucket objects

## Preparation for automation

* Clone this repository
* Execute `make install`
* Edit the configuration of the file `config.yaml`

## CI/CD Setup

The following steps are assumed to be executed in an environment either in the target project or in one that where the target project is accessible.

* Ensure the target project id is configured correctly in the environment variables (i.e. either `PROJECT_ID`, `_PROJECT_ID`, `PROJECTID` or `PROJECT`). This parameter can also be specified in the configuration file.
* Ensure that the Service Account for the Cloud Run Job exists and has sufficient rights against the list of services in scope. This is assuming you will not be using the default provided by GCP.
* Ensure that said Service Account has also `list` and `create` permissions to the target bucket
* Ensure that the target bucket exists and is accessible by the service account
* Ensure that the file `config.yaml` in the same directory as the makefile
* Execute `make deploy`

## Deployment dependencies

1. The bucket used to receive description artifacts must exist: it will not be created during the deployment process as this would imply granting more access to the user / service account performing the deployment.

2. The Service Account specified in the configuration file must exist and have the required permissions to all services listed in said configuration. For security reasons, the permissions granted to the service account must be limited to listing and viewing the inventory related to the services in scope.

## Update

By default, GCP mirrors the images from Docker Hub. The "latest" image from the mirror will often be out-of-sync with the one from Docker Hub.

In order to retain more control over the update process, the container version can be specified in the `config.yaml` configuration file.

The command `make deploy` will perform both initial creation of the deployment and also update an existing deployment.

## Configuration

Details of the configuration options are contained in the `config.yaml` file directly.

# Output files

## Strategy

* Produce one snapshot per execution of the Cloud Run Job `gcp-inventory`
* A `snapshot` consists of
  * One file object signaling the end of the snapshot execution `config.json`
  * One file object per service class `{SERVICE_CLASS}.json`
* A "latest.json" containing the reference to the latest snapshot
* No locking

## Organization

The files generated are uploaded to a specified Google Cloud Storage bucket.

Organization in the GCS bucket is as follows:

    {PROJECT_ID}/{TIMESTAMP}/config.json
    {PROJECT_ID}/{TIMESTAMP}/{SERVICE_CLASS}.json
    {PROJECT_ID}/latest.json

The `TIMESTAMP` is obtained at the start of the inventory (aka snapshot) process. Thus, all files prefixed with the same `TIMESTAMP` are issued from the same execution of the Cloud Run Job `gcp-inventory`.

The `config.json` contains the configuration is used to perform the inventory snapshot. The availability of this file also signals the end of the snapshot process.

## Timestamp

The format used is loosely based on ISO8601 with UTC as timezone: the "T" and "Z" characters are omitted and all other separators are by '-'. Example:

    2024-07-20-10-17-53


# Cloud Run Jobs

* https://cloud.google.com/run/docs/execute/jobs-on-schedule

# Architecture

In short, a script located in a Docker container executes a number of `gcloud $service list` commands in order to list the inventory of services / resources. Each entry is processed in order to remove sensitive information e.g. environment variables in Cloud Run services. This is accomplished by using `pygcloud`.

# Dependencies (major ones)

* [pygcloud](https://github.com/jldupont/pygcloud/)
* [Croniter](https://pypi.org/project/croniter/)
* [Fire](https://pypi.org/project/fire/)

# References

* [GCS Bucket Object listing](https://cloud.google.com/storage/docs/json_api/v1/objects/list#list-objects-and-prefixes-using-glob)
* [GCS naming](https://cloud.google.com/storage/docs/objects#naming)

# Future Enhancements

* Check IAM permissions on service account ahead of deploy / inventory processes
