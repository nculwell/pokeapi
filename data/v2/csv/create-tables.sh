#!/bin/sh

. common.sh

echo ".mode csv" > $SQL1

for csv in $CSV_FILES; do
  TABLE=$(basename "$csv" .csv)
  echo ".import $csv $TABLE" >> $SQL1
  echo ".schema $TABLE" >> $SQL1
done

rm -f $DB
sqlite3 -batch $DB < $SQL1 > $SQL2

#perl -pe 's/^(  [^,]+),/$1 primary key,/' < $SQL2 > $SQL3

#cat $SQL3

