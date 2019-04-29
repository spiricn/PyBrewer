#!/bin/bash

main() {
    # Script directory
    local scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

    # Timeout time before restarting upon crash
    local timeoutSec=10

    echo "watchdog started"

    # Loop forever
    while true; do
        echo "starting PyBrewer .."

        # Run application
        PYTHONPATH=${scriptDir}:$PYTHONPATH \
            python3 ${scriptDir}/brewer/App.py "$@"

        local rc=$?

        echo "PyBrewer stopped code=${rc}"

        if [  ${rc} == 0 ]; then
            # Exited cleanly, so stop watchdog..
            break
        elif [  ${rc} == 64 ]; then
            # Requested restart
            continue;
        fi

        # Application crashed, so sleep & restart
        echo "Re-starting in ${timeoutSec} sec"
        sleep ${timeoutSec}
    done

    echo "watchdog stopped"

    return $?
}

main "$@"

exit $?
