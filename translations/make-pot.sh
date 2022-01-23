#!/bin/bash

# creates apt-notifer.pot file 

MODULES=(
    ../lib/modules/apt-notifier.py  
    ../lib/modules/aptnotifier_xlate.py
    )

POTFILE=apt-notifier.pot
PKGNAME=apt-notifier
OPTS="--no-location --package-name=$PKGNAME -cTRANSLATORS:"
   
xgettext $OPTS -L Python -o $POTFILE "${MODULES[@]}"

sed -i 's/charset=CHARSET/charset=UTF-8/'  $POTFILE
