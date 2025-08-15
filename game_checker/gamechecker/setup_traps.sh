# to be sourced into another shell script

# set up a signal handlers for SIGINT (CTRL-C) and SIGTERM (kill $PID) that sends a TERM signal to the child processes

function signal_handler() {
	local signal=$1
	echo "$0: got SIG$signal"
	jobs=$(jobs -p)
	kill -TERM $jobs
	exit 1
}

trap_with_arg() {
    func="$1" ; shift
    for sig ; do
        trap "$func $sig" "$sig"
    done
}

trap_with_arg signal_handler INT TERM
