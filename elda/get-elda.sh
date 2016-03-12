#!/bin/sh

VERSION=1.3.17
DEST="elda-standalone-$VERSION-exec-war.jar"
DEST_SHA1SUM="44e462e77f9ab3935fec39c275c424e0695fab13 *$DEST"
URL="http://repository.epimorphics.com/com/epimorphics/lda/elda-standalone/$VERSION/elda-standalone-$VERSION-exec-war.jar"

echo "Calculating checksum for $DEST"
if echo "$DEST_SHA1SUM" | sha1sum -c -; then
    echo "$DEST exists, and checksum is fine, skipping download"
else
    echo "Re-downloading to $DEST"
    wget -O "$DEST" "$URL"
fi
