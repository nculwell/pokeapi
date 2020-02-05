#!/bin/sh

. ./common.sh

rm -f $DB
sqlite3 -batch $DB < create-tables-custom.sql

rm -f tablenames.txt
grep "^CREATE TABLE" create-tables-custom.sql | sed 's/CREATE TABLE //;s/(.*$//' > tablenames.txt
TABLES=$(cat tablenames.txt)

echo Creating headerless files.

echo ".mode csv" > $SQL4

for TABLE in $TABLES; do
  csv="$TABLE.csv"
  NOHEADER=NOHEADER_$csv
  tail -n+2 "$csv" > "$NOHEADER"
  echo ".import $NOHEADER $TABLE" >> $SQL4
done

sqlite3 -batch $DB < $SQL4

rm -f NOHEADER_*.csv

