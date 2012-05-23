#!/bin/sh -e

### BEGIN INIT INFO
# Provides:          django-mailserver
# Short-Description: django-mailserver service
### END INIT INFO


. /lib/lsb/init-functions

test $DEBIAN_SCRIPT_DEBUG && set -v -x

ROOT_FOLDER=`python <<EOF
import os
import mailserver
print os.path.dirname(mailserver.__file__)
EOF`

NAME=django-mailserver
PIDFILE=/var/run/$NAME.pid
DESC="email server for django webapps service"

start () {
    STATUS=0
    # Check to see if it's already started...
    if test -e $PIDFILE ; then
      log_failure_msg "Already running (PID file exists)"
    else
      python $ROOT_FOLDER/server.py
      echo $! > $PIDFILE
    fi
    log_end_msg $STATUS
}
stop () {
  kill `cat $PIDFILE` || true
  rm -f $PIDFILE
  log_end_msg 0
}

case "$1" in
start)
  log_action_begin_msg "Starting $NAME"

  start
  exit ${STATUS:-0}
  ;;
stop)
  log_action_begin_msg "Stopping $NAME"
  stop
  ;;
# Only 'reload'
reload|force-reload)
  log_action_begin_msg "Reloading $NAME"
  ;;
restart)
  stop
  start
  ;;
status)
  if test -e $PIDFILE ; then
    log_failure_msg "$NAME running (PID = `cat $PIDFILE`)"
  else
    log_failure_msg "$NAME stopped"
  fi
  ;;
*)
  echo "Usage: $0 {start|stop|reload|restart|status}" >&2
  exit 1
  ;;
esac

exit 0

# vim:set ai sts=2 sw=2 tw=0:
