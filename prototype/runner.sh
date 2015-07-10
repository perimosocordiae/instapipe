#!/usr/bin/env bash
vf=.view
cmd=''
while read -e -i "$cmd" -p '> ' cmd; do
  eval "$cmd | head 2>&1 >$vf"
done

