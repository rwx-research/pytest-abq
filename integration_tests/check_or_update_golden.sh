#!/bin/bash

# check_or_update_golden.sh update <file.json> adds the golden
# check_or_update_golden.sh <file.json> diffs it

if [[ "$1" == "update" ]]; then
  git add "$2"
else
  git diff --exit-code "$1"
fi
