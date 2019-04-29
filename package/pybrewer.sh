#!/bin/bash

PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin

### BEGIN INIT INFO
# Provides:          pybrewer
# Required-Start:    $local_fs $network $named $time $syslog
# Required-Stop:     $local_fs $network $named $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       PyBrewer
### END INIT INFO

SCRIPT=/usr/local/bin/pybrewer/pybrewer_runner.sh
RUNAS=pi

PIDFILE=/var/run/pybrewer.pid
LOGFILE=/var/log/pybrewer.log

log() {
    echo "$1" >&2
    echo "$1" >> /usr/local/bin/pybrewer/service.log
}

start() {
    if [ -f /var/run/$PIDNAME ] && kill -0 $(cat /var/run/$PIDNAME); then
        log 'Service already running'
        return 1
    fi

    log 'Starting service…'
    local CMD="$SCRIPT >/dev/null 2>&1 & echo \$!"
    su -c "$CMD" $RUNAS > "$PIDFILE"
    local pid=`cat ${PIDFILE}`

    log "Service started: ${pid}"
}

stop() {
    if [ ! -f "$PIDFILE" ]; then
        log 'Service not running'
        return 1
    fi

    local pid=`cat ${PIDFILE}`

    log 'Stopping service…'

    kill -15 ${pid}
    rm -f "$PIDFILE"

    log 'Service stopped'
}

restart() {
    log "Restarting service"

    stop
    start
}

case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
    restart)
        restart
    ;;
  *)
    log "Usage: $0 {start|stop|restart}"
esac