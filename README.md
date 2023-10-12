# Disk Usage

Periodically checks disk usage of mounted file systems and presents them via
a Prometheus compatible metrics interface

## What's inside ?

The image is based on the `python:3.11-slim-bookworm` image and incorperates these major components:

* [parallel-disk-usage](https://github.com/KSXGitHub/parallel-disk-usage/)

## How to get started

1. Install python 3.11
2. Create a virtual environment
`python3 -m venv .venv`
3. Install requirements
`pip install -r requirements`
4. Code away!

Keep in mind that this project uses https://github.com/KSXGitHub/parallel-disk-usage/
and requires the pdu binary in PATH.


## How to test local

The docker image can be tested locally without the need of a Kubernetes environment.

1. Copy the `.env.sample` to `.env`
2. Start the containers using docker compose:
```
docker compose build
docker compose up
```
3. Visit http://localhost:8000/metrics to review metrics.

You can also use this method to code and debug live within docker.

## Environment variables

The following environment variables can be adjusted depending on requirements.

| Variable | Description | Valid values | Default
---|---|---|---|
USAGE_LOOP_MODE | Mode we want to loop for disk usage runs | day or second | day
USAGE_LOOP_TIME | Value for the loop mode | integer second or time string | 16:00
USAGE_LOOP_TIMEZONE | If the loop needs to be timezone aware | timezone string | UTC
ROOT_FOLDER | Root folder to run the disk usage | string | mnt
EXPORT_REPORTING_DEPTH | Export reporting depth | integer | 0
FOLDER_REPORTING_DEPTH | Depth for the folder disk usage | integer | 2 
USE_LOCAL_STATE | Whether to use a local state usage file  | boolean | False
USE_KUBE_STATE | Whether to use a Kube secret object to store usage state | boolean | True
KUBE_USAGE_KEY | Name of the key in the Kube secret | string | usage.json
USE_KUBE_CONFIG | Whether to use in cluster config or kube config file at ~/.kube/config | boolean | False
KUBE_USAGE_SECRET | Name of the Kube secret to store usage data | string | folder-disk-usage
USAGE_FILE | Name of the local usage file to store or cache usage data | string | No value
CACHED_READ_THRESHOLD_SECONDS | Seconds to use local usage file for cache | integer | 300
API_WORKERS | Number of API workers to use | integer | 2
API_PORT | Port to listen on for the API | integer | 8000
API_HOST | Address to bind to for the API | string | 0.0.0.0
CREATE_FAKE_DATA | Whether to create fake data at the mount point for testing | boolean | False

## License

This project is licensed under Apache License 2.0
