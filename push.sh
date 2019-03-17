#!/bin/bash

main() {
    rsync -avHe ssh `pwd` pi@192.168.0.19:/home/pi/dev/PyBrewer --exclude .git --exclude app
}

main "$@"

