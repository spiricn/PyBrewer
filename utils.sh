#!/bin/bash

pb_serve_fe() {
    pushd ${PB_ROOT}/frontend

    local ip=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`

    ng serve --host ${ip}

    popd
}

pb_push() {
    pushd ${PB_ROOT}

    rsync -avHe ssh `pwd` \
        ${PB_REMOTE_DEVICE}:${PB_REMOTE_LOCATION} \
        --exclude .git \
        --exclude frontend

    popd
}

main () {
    export PB_ROOT=$(cd "$(dirname "$0")"; pwd)
    export -f pb_serve_fe
    export -f pb_push
}

main "$@"