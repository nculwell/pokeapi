#!/bin/bash

THIS_MONTH=$(date "+%Y-%m")

for y in $(seq 2014 2020); do
  for m in $(seq 1 12); do
    MONTH=$(printf "%d-%02d" "$y" "$m")
    [[ "$MONTH" < "2014-11" ]] && continue
    [[ "$MONTH" < "$THIS_MONTH" ]] || continue
    for format in lc ou ubers uu nu doublesou; do
      for wt in 0 1500 1630 1760; do
        USAGE_URL="https://www.smogon.com/stats/$MONTH/gen4$format-$wt.txt"
        if wget -q -c -nc --force-directories "$USAGE_URL"; then
          echo "SUCC: $USAGE_URL"
          for subdir in moveset metagame leads; do
            SUBDIR_URL="https://www.smogon.com/stats/$MONTH/$subdir/gen4$format-$wt.txt"
            wget -q -c -nc --force-directories "$SUBDIR_URL" || echo FAIL: $SUBDIR_URL && echo SUCC: $SUBDIR_URL
          done
        else
          echo "FAIL: $USAGE_URL"
        fi
      done
    done
  done
done

