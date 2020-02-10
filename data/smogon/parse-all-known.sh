#!/bin/bash

if [ -z "$1" ] || [ -d "www.smogon.com/stats/$1" ]; then

  find "www.smogon.com/stats/$1" -path "*/moveset/*" -name "*.txt" -exec "$0" "{}" ";"

else

  MOVESET_FILENAME="$1"
  LEADS_FILENAME="$(echo "$MOVESET_FILENAME" | sed 's|/moveset/|/leads/|')"
  echo "$MOVESET_FILENAME, $LEADS_FILENAME"
  echo Parsing: $MOVESET_FILENAME
  ./parse-moveset.py "$MOVESET_FILENAME"
  if [ -f "$LEADS_FILENAME" ]; then
    echo Parsing: $LEADS_FILENAME
    ./parse-leads.py "$LEADS_FILENAME"
  else
    echo "Missing: $LEADS_FILENAME"
  fi

fi

