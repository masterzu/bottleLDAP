#!/bin/bash

FILES="README.rst server.py"

usage () {
    cat <<EOT
Usage: $(basename $0) <REL_VERSION> 

Change in files ($FILES) all :
- "@VERSION@" with  "<REL_VERSION>"
- "@DATE@" with  "<REL_DATE>"
EOT
    exit 1
}

debug () {
    return
    echo "DEBUG: $@"
}

test -z "$1" && usage 
VERSION="$1"
DATE=$(date '+%d %b %Y')

debug VERSION: $VERSION
debug DEBUG DATE: $DATE

### files to transform
for sc in $FILES
do 
    ds=$(mktemp);
    script=$(mktemp)
    rm -f $ds; 
    echo -n "changing $sc ... "; 
    debug "sc:     $sc"
    debug "ds:     $ds"
    debug "script: $script"
    rm -f $script; 
    echo "s!@VERSION@!$VERSION!;" >> $script; 
    echo "s!@DATE@!$DATE!;" >> $script; 
    echo 'w' $ds >> $script; 
    sed --quiet -f $script $sc && { mv "$ds" "$sc"; echo "OK"; } || { echo "Error on changing file $sc with script $script"; exit 1; }
    rm -f $script;
done

exit 0
