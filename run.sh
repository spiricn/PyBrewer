#!/bin/bash

main() {
    cfgPath=$1

    PYTHONPATH=`pwd`:$PYTHONPATH python3 `pwd`/brewer/App.py ${cfgPath}

    return $?
}

main "$@"

