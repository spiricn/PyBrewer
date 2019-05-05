#!/bin/bash

#
# Serve FE app locally
#
pb_serve_fe() {
    pushd ${PB_ROOT}/frontend

    local ip=`ip route get 1.2.3.4 | awk '{print $7}'`

    ng serve --host ${ip}

    popd
}

#
# Push everything to target device
#
pb_push() {
    pushd ${PB_ROOT}

    rsync -avHe ssh `pwd` \
        ${PB_REMOTE_DEVICE}:${PB_REMOTE_LOCATION} \
        --exclude .git \
        --exclude frontend \
        --exclude doc \
        --exclude android

    popd
}

main () {
    export PB_ROOT=$(cd "$(dirname "$0")"; pwd)
    export -f pb_serve_fe
    export -f pb_push
}

main "$@"
