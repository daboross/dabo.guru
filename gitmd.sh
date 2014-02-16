#!/bin/bash
#  mc - Minecraft Server Script
#
# ### License ###
#
# Copyright 2013 Dabo Ross
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

### Configuration ###

declare -r NAME="gitmd-data"

### Script Variables ###

# Set THIS to be this script.
declare -r SCRIPT="$([[ $0 = /* ]] && echo "$0" || echo "$PWD/${0#./}")"

# Storage vars
declare -r PID_FILE="${HOME}/${NAME}/.server-pid"
declare -r SCRIPT_DISABLED_FILE="${HOME}/${NAME}/.script-disabled"

### Script Functions ###

# Resumes the server session
resume() {
    if tmux has-session -t "${NAME}-server" &> /dev/null; then
        tmux attach -t "${NAME}-server"
    else
        echo "No server session exists"
    fi
}

# Gets the current log file
# stdout - log file
get_log() {
    local -r LOG_DIR="${HOME}/${NAME}/logs"
    mkdir -p "$LOG_DIR"
    local -r LOG_FILE="${LOG_DIR}/$(date +%Y-%m-%d).log"
    touch "$LOG_FILE"
    echo "$LOG_FILE"
}

# Logs something to the log file
# $@ - Lines to log
log() {
    echo "$@"
    echo "$(date +'%Y/%m/%d %H:%M') [${1}] ${@:2}" >> "$(get_log)"
}

# Tests if the server is running
# stdout - true if running
server_running() {
    [[ -a "$PID_FILE" ]] || return 1
    local -r SERVER_PID="$(cat ${PID_FILE})"
    kill -s 0 "$SERVER_PID" &> /dev/null && return 0 || return 1
}

# Runs the server script
server_script() {
    if script_enabled; then
        if server_running; then
            log "server_script" "Server running"
        else
            log "server_script" "Restarting server"
            restart_server
        fi
    else
        log "server_script" "Script disabled"
    fi
}

boot() {
    log "boot" "Running"
    start_server
}

script_enabled() {
    [[ -a "$SCRIPT_DISABLED_FILE" ]] && return 1 || return 0
}

disable_script() {
    if [[ -a "$SCRIPT_DISABLED_FILE" ]]; then
        log "disable_script" "Script already disabled"
    else
        log "disable_script" "Disabling script"
        mkdir -p "$(dirname ${SCRIPT_DISABLED_FILE})"
        touch "$SCRIPT_DISABLED_FILE"
    fi
}

enable_script() {
    if [[ -a "$SCRIPT_DISABLED_FILE" ]]; then
        log "enable_script" "Enabling script"
        rm -f "$SCRIPT_DISABLED_FILE"
    else
        log "enable_script" "Script already enabled"
    fi
}

# Kills the server
kill_server() {
    local -r SERVER_PID="$(cat ${PID_FILE})"
    log "kill_server" "Starting"
    kill "$SERVER_PID" &> /dev/null
    timeout="$((10 + $(date '+%s')))"
    while server_running; do
        if [[ "$(date '+%s')" -gt "$timeout" ]]; then
            kill -9 "$SERVER_PID" &> /dev/null
        fi
        sleep 1s
    done
    log "kill_server" "Done"
}

# Kills the server then starts it
restart() {
    log "kill_start" "Starting"
    kill_server
    start_server
    log "kill_start" "Done"
}

# Starts the server!
start_server() {
    if server_running; then
        log "start_server" "Server already running"
    else
        log "start_server" "Starting server"
        if [[ "$TMUX" ]]; then
            local -r TMUX_BAK="$TMUX"
            unset "TMUX"
        fi
        tmux new -ds "${NAME}-server" "'$SCRIPT' internal-start"
        if [[ "$TMUX_BAK" ]]; then
            TMUX="$TMUX_BAK"
        fi
        enable_script
    fi
}

# Internally used start function
internal_start() {
    cd "$HOME/gitmd/"
    local -r SERVER_PID="$$"
    echo "$SERVER_PID" > "$PID_FILE"
    log "internal_start" "Starting with pid $SERVER_PID"
    exec python3 main.py
}

# Stops the server, then starts it
stop_start() {
    log "stop_start" "Starting"
    disable_script
    kill_server
    start_server
    log "stop_start" "Done"
}

# Views the log file with 'tail'
view_log() {
    local LENGTH="$1"
    if [[ -z "$LENGTH" ]]; then
        LENGTH="100"
    fi
    tail -n "$LENGTH" "$(get_log)"
}

### Commmand line function

cmd_help() {
    echo " ---- mc - ${NAME} ----"
    echo " status         - Gives the server's status"
    echo " resume         - Resumes the server session"
    echo " start-server   - Starts the server"
    echo " stop-server    - Stops the server"
    echo " restart        - Stops the server, then starts it"
    echo " kill-server    - Kills the server"
    echo " kill-start     - Kills the server then starts it"
    echo " view-log       - Views the script log"
    echo " check-script   - Starts it if it isn't online"
    echo " script-enabled - Checks if the check-script is enabled"
    echo " enable-script  - Enables the check-script"
    echo " disable-script - Disable the check-script"
    if [[ "$1" == "--internal" ]]; then
        echo " ---- Internally used / debug commands ----"
        echo " boot                 - Script to run at boot"
        echo " internal-start       - Internal start script"
     fi
}

main() {
    local -r FUNCTION="$1"
    local -r P="[${NAME}]"
    case "$FUNCTION" in
        resume)
            resume ;;
        status)
            if server_running; then
                echo "Server $NAME running!"
                return 0
            else
                echo "Server $NAME not running."
                return 1
            fi ;;
        check-script)
            server_script ;;
        boot)
            boot ;;
        script-enabled)
            if script_enabled; then
                echo "Script is enabled"
                return 0
            else
                echo "Script is disabled"
                return 1
            fi ;;
        enable-script)
            enable_script ;;
        disable-script)
            disable_script ;;
        stop)
            kill_server ;;
        restart)
            restart ;;
        start)
            start_server ;;
        view-log)
            view_log ;;
        help)
            cmd_help "$1" ;;
        internal-start)
            internal_start ;;
        ?*)
            echo "Unknown argument '${1}'"
            cmd_help ;;
        *)
            cmd_help ;;
    esac
}
main "$@"
