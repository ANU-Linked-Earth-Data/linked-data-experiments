#!/bin/bash

set -e

. get-virtuoso.sh
echo "Running Virtuoso"
"$PREFIX/bin/virtuoso-t" +foreground +configfile virtuoso.ini
