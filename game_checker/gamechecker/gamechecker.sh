#!/bin/bash

USAGE=$(cat <<ENDUSAGE
$0 [--gdl-version=(1|2)] [--dfs-time=SECONDS] [--mc-time=SECONDS] gamefile.kif

    Checks gamefile.kif for syntactic and semantic problems.

    --dfs-time=SECONDS .. SECONDS seconds are spent doing a depth-first search
                          of the game to find non-playable states, loop, etc.
                          (default: 0)
    --mc-time=SECONDS  .. SECONDS seconds are spent doing Monte Carlo simulations
                          of the game to find non-playable states, loop, etc.
                          (default: 0)
    --gdl-version=2    .. the game is also checked for the following properties:
                          - each player knows his legal moves in every state
                          - each player knows when the game is over
                          - each player knows his reward, when the game is over
                          (default: 1)
ENDUSAGE
)

if [[ "$*" == "" ]]; then
	echo "$USAGE"
	exit 0
fi

GDL_VERSION=1
DFS_TIME=0
MC_TIME=0
# parse command line arguments
for arg in $*
do
	case $arg in
    	--gdl-version=*)
			GDL_VERSION=${arg#*=}
		;;
    	--dfs-time=*)
			
			DFS_TIME=${arg#*=}
		;;
		--mc-time=*)
			MC_TIME=${arg#*=}
		;;
    	--*)
			echo "unknown option: $arg"
			echo "$USAGE"
			exit -1
		;;
    	*)
			GAMEFILE=$arg
		;;
  	esac
done

echo "starting eclipse ...";
timeout=$(( 10 + ${DFS_TIME} + ${MC_TIME} ))
check_gdl_options="[dfs_check_time:${DFS_TIME}, random_check_time:${MC_TIME}, maxdepth:1000, gdl_version:${GDL_VERSION}]";
./game_checker/gamechecker/run_eclipse.sh $timeout 1048576 -- -e "set_stream_property(output, flush, end_of_line), set_stream_property(error, flush, end_of_line), ensure_loaded(\"game_checker/gamechecker/prolog/game_checker/game_description_checker\"), open(\"$GAMEFILE\",read,Stream), read_string(Stream, end_of_file, _, GDL), close(Stream), game_description_checker:check_gdl(GDL, ${check_gdl_options})"
