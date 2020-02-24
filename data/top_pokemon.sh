#!/bin/sh

STATS="hp attack defense special-attack special-defense speed"

rm -f TEMP.SQL
for s in $STATS; do
  sed "s/special-defense/$s/" < top_pokemon.sql > TEMP.SQL
  STAT_NAME=$(echo "$s" | sed 's/-//g')
  sqlite3 pokeapi.db < TEMP.SQL | sed 's/|/ /g' | head -n100 > pokemon_by_$STAT_NAME.txt
  rm -f TEMP.SQL
done

