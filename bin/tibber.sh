#!/bin/bash

. $LBHOMEDIR/libs/bashlib/loxberry_log.sh

# Create Path in Ramdisc
LBPCONFIGDIR=$(perl -e 'use LoxBerry::System; print $lbpconfigdir; exit;')
TMPPATH=$(jq -r '.path' $LBPCONFIGDIR/plugin.json)
mkdir -p $TMPPATH

# Logging
LBPLOGDIR=$(perl -e 'use LoxBerry::System; print $lbplogdir; exit;');
PACKAGE=tibber_display
NAME=Daemon
LOGDIR=$LBPLOGDIR

LOGSTART "Tibber_display started: $@"

# Start Tibber script
python3 tibber.py $@ > ${FILENAME}
