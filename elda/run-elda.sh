#!/bin/sh

. ./get-elda.sh
java -jar "$DEST" -Delda.spec=lde-config.ttl $@
