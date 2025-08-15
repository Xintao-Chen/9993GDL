#!/bin/bash

if [ ! -r ./game_checker/gamechecker/setup_env.sh ] ; then
	echo "Run \"make\" first to create setup_env.sh!"
	exit 1
fi
. ./game_checker/gamechecker/setup_env.sh

. ./game_checker/gamechecker/setup_traps.sh

timelimit="";
if [[ "$1" != "--" ]]; then
	timelimit=$1 # the timelimit in seconds
	shift
fi
memorylimit="";
if [[ "$1" != "--" ]]; then
	memorylimit=$1 # the memory limit in kbytes
	shift
fi
while [[ "$1" != "--" && ! -z "$1" ]]; do
	echo "ignoring argument $1"
	shift
done
shift

if [[ ! -z "$memorylimit" ]] ; then
	echo "limiting virtual memory to $memorylimit kbytes"
	ulimit -Sv $memorylimit
	ulimit -Hv $memorylimit
fi

if [[ ! -z "$timelimit" && "$timelimit" -gt 0 ]] ; then
	echo "limiting cpu time to $timelimit seconds"
	ulimit -St $timelimit
	ulimit -Ht $timelimit
fi

$ECLIPSE "$@" &
# putting in background and waiting is necessary for "trap xxx TERM" to work
wait $! || echo "eclipse returned with status $?"
