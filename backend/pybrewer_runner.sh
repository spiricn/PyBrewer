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


        local appPath=${scriptDir}/brewer/App.py

        if [ -f $appPath ]; then
            # Run application from source code
            PYTHONPATH=${scriptDir}:$PYTHONPATH \
                python3 ${scriptDir}/brewer/App.py "$@"
        else
            # Run application from executable
            ${scriptDir}/pybrewer
        fi

        local rc=$?

        echo "PyBrewer stopped code=${rc}"

        if [  ${rc} == 0 ]; then
            # Exited cleanly, so stop watchdog..
            break
        elif [  ${rc} == 64 ]; then
            # Requested restart by return error code 64
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
