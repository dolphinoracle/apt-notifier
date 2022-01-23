#!/bin/bash

echodo() {
  echo "${@}"
  ${@}
}

# prepare transifex 
if [ ! -s  .tx/config ]; then
   mkdir -p .tx
   cat <<EOF > .tx/config
[main]
host = https://www.transifex.com

[antix-development.apt-notifier]
file_filter = po/<lang>/apt-notifier.po
minimum_perc = 0
source_file = apt-notifier.pot
source_lang = en
type = PO
EOF
fi    

# backup existing
[ -d po ] && echodo mv po po_$(date '+%Y-%m-%d_%H%M%S').bak

# get all translations
if command -v tx >/dev/null; then
   echodo tx pull --all
fi

