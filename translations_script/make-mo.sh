#!/bin/bash

echodo() {
  echo "${@}"
  ${@}
}
# backup existing
[ -d mo ] && echodo mv mo mo_$(date '+%Y-%m-%d_%H%M%S').bak

for PO in po/*/*.po; do 
  MO=${PO//po/mo}
  echodo mkdir -p ${MO%/*}; 
  echodo msgfmt -o $MO $PO
done 

