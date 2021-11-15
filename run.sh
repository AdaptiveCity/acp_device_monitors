SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR
pid=$(pgrep -f "python3 start_monitors.py")
if [ $? -eq 0 ]
then
    echo $(date '+%s') start_monitors.py already running as PID $pid
    exit 1
else
    echo $(date '+%s') starting monitors
    nohup python3 start_monitors.py >/var/log/acp_prod/acp_monitors.log 2>/var/log/acp_prod/acp_monitors.err </dev/null & disown
    exit 0
fi

