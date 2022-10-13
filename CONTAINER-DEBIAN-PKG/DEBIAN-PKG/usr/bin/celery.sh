#!/bin/bash

app=api
workdir=/var/www/api
logLevel=INFO

# Options:
# --max-tasks-per-child: at the end of the task terminate the worker and replace it with a new one.
#     This avoids the problem of having an increasing number of open connections toward the vCenter.
#

function start()
{
    if [ -x /var/lib/api-venv/bin/celery ]; then
        /var/lib/api-venv/bin/celery --app $app --workdir $workdir worker -l $logLevel --hostname api@%h --autoscale 2,10 --max-tasks-per-child 1
    else
        celery --app $app --workdir $workdir worker -l $logLevel --hostname api@%h --autoscale 2,10 --max-tasks-per-child 1
    fi
}

function stop()
{
    PS=$(ps axu|grep -P 'celery' | grep -v 'grep' | awk '{print $2}')
    if [ -n "$PS" ]; then
        kill $PS
    fi
}

function restart()
{
    stop
    sleep 1
    start
}

function status()
{
    celery --app $app --workdir $workdir inspect stats
}

case $1 in
        start)
            start
            ;;

        stop)
            stop
            ;;

        restart)
            stop
            start
            ;;

        status)
            status
            ;;

        *)
            echo $"Usage: $0 {start|stop|restart|status}"
            exit 1
esac

exit 0
