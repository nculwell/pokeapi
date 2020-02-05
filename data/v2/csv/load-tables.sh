#!/bin/sh

. common.sh

rm -f $DB
sqlite3 -batch $DB < $SQL3

echo Creating headerless files.

echo ".mode csv" > $SQL4

for csv in $CSV_FILES; do
  TABLE=$(basename "$csv" .csv)
  NOHEADER=NOHEADER_$csv
  tail -n+2 "$csv" > "$NOHEADER"
  echo ".import $NOHEADER $TABLE" >> $SQL4
done

sqlite3 -batch $DB < $SQL4

rm -f NOHEADER_*.csv

