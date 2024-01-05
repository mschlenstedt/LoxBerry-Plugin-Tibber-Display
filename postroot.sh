#!/bin/bash
 
# You can use all vars from /etc/environment in this script.
#
# We add 5 additional arguments when executing this script:
# command <TEMPFOLDER> <NAME> <FOLDER> <VERSION> <BASEFOLDER>
#
# For logging, print to STDOUT. You can use the following tags for showing
# different colorized information during plugin installation:
#
# <OK> This was ok!"
# <INFO> This is just for your information."
# <WARNING> This is a warning!"
# <ERROR> This is an error!"
# <FAIL> This is a fail!"
 
# To use important variables from command line use the following code:
COMMAND=$0    # Zero argument is shell command
PTEMPDIR=$1   # First argument is temp folder during install
PSHNAME=$2    # Second argument is Plugin-Name for scipts etc.
PDIR=$3       # Third argument is Plugin installation folder
PVERSION=$4   # Forth argument is Plugin version
#LBHOMEDIR=$5 # Comes from /etc/environment now. Fifth argument is
              # Base folder of LoxBerry
PTEMPPATH=$6  # Sixth argument is full temp path during install (see also $1)
 
# Combine them with /etc/environment
PHTMLAUTH=$LBPHTMLAUTH/$PDIR
PHTML=$LBPHTML/$PDIR
PTEMPL=$LBPTEMPL/$PDIR
PDATA=$LBPDATA/$PDIR
PLOG=$LBPLOG/$PDIR # Note! This is stored on a Ramdisk now!
PCONFIG=$LBPCONFIG/$PDIR
PSBIN=$LBPSBIN/$PDIR
PBIN=$LBPBIN/$PDIR

echo "<INFO> Installing Matplotlib via pip..."
if [ ! -e /tmp_pip ]; then
	mkdir -p /tmp_pip
 	REMOVE=1
fi
yes | TMPDIR=/tmp_pip python3 -m pip install matplotlib
if [ $REMOVE -eq 1 ]; then
	rm -r /tmp_pip
fi

INSTALLED_ST=$(python3 -m pip list --format=columns | grep -i "matplotlib" | grep -v grep | wc -l)
if [ ${INSTALLED_ST} -ne "0" ]; then
	echo "<OK> Matplotlib installed successfully."
else
	echo "<FAIL> Matplotlib could not be installed."
	exit 2;
fi

echo "<INFO> Creating needed German locale..."
localedef -i de_DE -f UTF-8 de_DE.UTF-8
locale -a

# Exit with Status 0
exit 0
