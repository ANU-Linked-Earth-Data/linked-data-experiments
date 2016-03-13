#!/bin/sh

. ./get-elda.sh
# Head to http://localhost:8080/standalone/accidents to see what's there.
java -jar "$DEST" -Delda.spec "$(pwd)/lde-config.ttl" $@
