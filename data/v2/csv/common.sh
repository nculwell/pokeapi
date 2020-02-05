#!/bin/sh

CSVLIST=csvlist.txt
DB=pokedex.db
SQL1=import1.sql
SQL2=create-tables.sql
SQL3=import3.sql
SQL4=import4.sql

rm -f $DB $SQL1 $SQL2 $SQL3 $SQL4 $CSVLIST

CSV_FILES=$(find *.csv ! -name '*flavor_text*' ! -name '*prose*' ! -name 'NOHEADER_*')
for csv in $CSV_FILES; do
  # remove empty files (header line only)
  [ "$(wc -l "$csv" | cut -d' ' -f1)" -gt 1 ] || continue
  echo $csv >> $CSVLIST
done
CSV_FILES=$(cat $CSVLIST)
#rm -f $CSVLIST
#echo INCLUDING FILES: $CSV_FILES >&2

