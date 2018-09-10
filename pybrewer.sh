#!/bin/bash

main() {
    local root="/home/pi/dev/PyBrewer/PyBrewer"

    local scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

    local timeoutSec=10

    echo "watchdog started"

    while true; do
        echo "starting PyBrewer .."

        PYTHONPATH=${scriptDir}:$PYTHONPATH \
            python3 ${scriptDir}/brewer/App.py "$@"

        local rc=$?

        echo "PyBrewer stopped code=${rc}"

        if [  ${rc} == 0 ]; then
            break
        fi

        echo "Re-starting in ${timeoutSec} sec"
        sleep ${timeoutSec}
    done

    echo "watchdog stopped"

    return $?
}

main "$@"

