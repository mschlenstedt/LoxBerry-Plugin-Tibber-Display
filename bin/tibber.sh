#!/bin/bash

. $LBHOMEDIR/libs/bashlib/loxberry_log.sh

# Create Path in Ramdisc
LBPCONFIGDIR=$(perl -e 'use LoxBerry::System; print $lbpconfigdir; exit;')
LBPHTMLDIR=$(perl -e 'use LoxBerry::System; print $lbphtmldir; exit;')
TMPPATH=$(jq -r '.path' $LBPCONFIGDIR/plugin.json)
mkdir -p $TMPPATH
if [ ! -e "$LBPHTMLDIR/data" ]; then
	ln -s /dev/shm/tibber_display/ $LBPHTMLDIR/data
fi

# Logging
LBPLOGDIR=$(perl -e 'use LoxBerry::System; print $lbplogdir; exit;');
PACKAGE=tibber-display
NAME=Grabber
LOGDIR=$LBPLOGDIR
LOGLEVEL=7

LOGSTART "Tibber-Display Grabber started..."
LOGINF "Commandline options: $@"
LOGOK "Starting Tibber Grabber Script..."

# Start Tibber script
LBPBINDIR=$(perl -e 'use LoxBerry::System; print $lbpbindir; exit;')
python3 $LBPBINDIR/tibber.py $@ >> ${FILENAME} 2>&1

LOGEND "Processing successfully finished"
