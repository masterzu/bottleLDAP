#!/bin/bash -e

# make a release script from git-clone to git push to master

# A small LDAP admin site
# https://github.com/masterzu/bottleLDAP
# Copyright (C) 2013-2016  Patrick Cao Huu Thien <patrick.cao_huu_thien@upmc.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# make a release script

# A small LDAP admin site
# https://github.com/masterzu/bottleLDAP
# Copyright (C) 2013-2016  Patrick Cao Huu Thien <patrick.cao_huu_thien@upmc.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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

# debug VERSION: $VERSION
# debug DATE: $DATE

## make new git branch
git checkout -b "v$VERSION"

## install devel tools
npm install

## running python test and run tests
python server.py -M config_test.ini &
npm test
kill %1

## add new files
git add static/all.min.js static/all.css

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

## add modified files
git add $FILES

## clean all devel files
git rm Gruntfile.js package.json bower.json
git rm -r grunt_files/
git rm -r tests/


cat <<EOT
OK

Release v$VERSION allmost done.

things to do:

* commit

  git commit -a -m '$VERSION'

* merge from master

  git checkout master
  git merge v$VERSION

* resolve merge conflics
  
  git mergetool

* commit and push

  git commit
  git push

EOT


exit 0
