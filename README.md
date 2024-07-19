# gcp-inventory

This project is about exporting an inventory of descriptions related to service instances & resources from a GCP project.

The inventory can be used in different ways, e.g.:

* Draw a diagram representing relationships between entities
* Perform policy related processes

# Security & Privacy

The standard setup is totally under the control of the user.
There is a capability to filter-out information to any granularity deemed required.

# Usage

## Planning

Usually, an SDLC process for governing application lifecycle is leveraged. In this context, it is best practice to have multiple environments (aka `projects`) in a `workload` (i.e. collection of projects).

From the above, it is reasonable one would want to use `gcp-inventory` on all projects in the workload. Thus, the following steps are assumed:

* Choose a project where the target GCS bucket will provisioned (e.g. the '-src' project along with source code)
* Further to the previous point, consider using a separate project if you plan to expose the bucket to a third party. This step is not strictly required: it really depends on your risk appetite. Properly securing a GCS bucket is fairly straightforward now.

## Preparation for automation

* Clone this repository
* Execute `make install`
* Edit the configuration of the file `config.yaml`

## CI/CD Setup

The following steps are assumed to be executed in an environment either in the target project or in one that where the target project is accessible.

* Ensure the target project id is configured correctly in the environment variables (i.e. either `PROJECT_ID`, `_PROJECT_ID` or `PROJECT`)
* Ensure that the Service Account for the Cloud Run Job exists and has sufficient rights against the list of services in scope
* Ensure that said Service Account has also `list` and `create` permissions to the target bucket
* Ensure that the file `config.yaml` in the same directory as the makefile
* Execute `make deploy`

## Deployment dependencies

1. The bucket used to receive description artifacts must exists: it will not be created during the deployment process as this would imply granting more access to the user / service account performing the deployment.

2. The Service Account specified in the configuration file must exist and have the required permissions to all services listed in said configuration. For security reasons, the permissions granted to the service account must be limited to listing and viewing the inventory related to the services in scope.

If the target GCS bucket does not exists, the script will fail.

## Update

TODO

## Configuration

Details of the configuration options are contained in the `config.yaml` file directly.

# Output files

The files generated are uploaded to a specified Google Cloud Storage bucket.

Organization in the GCS bucket is as follows:

* 

# Cloud Run Jobs

* https://cloud.google.com/run/docs/execute/jobs-on-schedule

# Architecture

In short, a script located in a Docker container executes a number of `gcloud $service list` commands in order to list the inventory of resources. Each entry is processed in order to remove sensitive information e.g. environment variables in Cloud Run services.

## Solution

The solution leverages the python package [pygcloud](https://github.com/jldupont/pygcloud/).

1. The script verifies if a `configuration file` is present in the configured path
1. The script reads the list of enabled services in the target project if no configuration file is present
1. For each `service`, the script verifies if a `handler` is available
1. Each `handler`, lists the service instances in the target project in JSON representation
1. Then the `handler` instantiates a `pygcloud` class object associated with the service instance
1. Finally, each `pygcloud` object is written, in JSON format, to a file in the configured path


# Dependencies

* [pygcloud](https://github.com/jldupont/pygcloud/)
