# setup some environment variables for running eclipse

ECLIPSE_DIR="/srv/scratch/z5485311/GDL2NL/Eclipse"
ECLIPSE_GLOBAL_STACK="512"
ECLIPSE_LOCAL_STACK="128"
ARCH="x86_64_linux"

ECLIPSE_BIN_DIR="${ECLIPSE_DIR}/bin/${ARCH}"
ECLIPSE="${ECLIPSE_BIN_DIR}/eclipse -l ${ECLIPSE_LOCAL_STACK}M -g ${ECLIPSE_GLOBAL_STACK}M"
ECLIPSE_CLASSPATH="${ECLIPSE_DIR}/lib/eclipse.jar:${ECLIPSE_DIR}/lib/visualisation.jar"


