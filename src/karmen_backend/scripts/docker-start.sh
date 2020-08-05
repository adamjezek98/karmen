#!/bin/bash

err() {
  echo "ERROR: $@" >&2
}

trap 'exit_code=$?; err "Exiting on error $exit_code"; exit $exit_code' ERR
set -o errtrace # print traceback on error
set -o pipefail  # exit on error in pipe


echo "Starting backend service $SERVICE in mode '$ENV'"


python3 ./karmen/manage.py migrate
python3 ./karmen/manage.py generate_test_data
python3 ./karmen/manage.py runserver 0.0.0.0:8000


echo "Starting backend service $SERVICE in mode '$ENV'"
