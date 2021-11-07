#!/bin/bash
set -e

# Before running this script build the image
# podman build -t homemanager-test-f34 -f Dockerfile.fedora-34 .
CONTAINER=homemanager-test-f34
IMAGE=homemanager-test-f34
TESTS_DIRECTORY=$(dirname "$(readlink -f "$0")")
ROOT_DIRECTORY=$(dirname "$TESTS_DIRECTORY")

podman run -d --name $CONTAINER $IMAGE
until podman exec $CONTAINER systemctl status | grep running
do
    echo '>>> Wait container to start'
    sleep 1
done
podman exec $CONTAINER postgresql-setup --initdb
podman exec $CONTAINER systemctl enable --now postgresql
podman exec -u postgres $CONTAINER createuser hmuser
podman exec -u postgres $CONTAINER createdb testdb --owner=hmuser

podman cp "$ROOT_DIRECTORY/homemanager/." "$CONTAINER:/homemanager/homemanager"
podman cp "$ROOT_DIRECTORY/db_manage.py" "$CONTAINER:/homemanager/db_manage.py"
podman cp "$ROOT_DIRECTORY/run_home_manager.py" "$CONTAINER:/homemanager/run_home_manager.py"
podman cp "$ROOT_DIRECTORY/video-test/." "$CONTAINER:/homemanager/video-test"
podman cp "$ROOT_DIRECTORY/motion-test/." "$CONTAINER:/homemanager/motion-test"
podman cp "$TESTS_DIRECTORY/test_api" "$CONTAINER:/homemanager/tests/test_api"
podman cp "$TESTS_DIRECTORY/conf.pytest-container.py" "$CONTAINER:/homemanager/homemanager/conf.py"
podman exec $CONTAINER find /homemanager/homemanager -name '__pycache__' -type d -exec rm -r {} +

podman exec -u hmuser $CONTAINER /homemanager/db_manage.py init-db
# `cmd || true` masks non-zero exit code of cmd, it is needed for future
# stop and rm commands when `set -e` is used
podman exec -u hmuser -w /homemanager $CONTAINER \
  python3 -m pytest tests/test_api -W ignore::DeprecationWarning -p no:cacheprovider \
  || true

podman container stop $CONTAINER
podman container rm $CONTAINER
