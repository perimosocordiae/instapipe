#!/usr/bin/env bash

vf=.view

if [[ ! -e "$vf" ]]; then touch "$vf"; fi

while read; do
  clear
  cat "$vf"
done < <(inotifywait -mq -e close_write "$vf")

