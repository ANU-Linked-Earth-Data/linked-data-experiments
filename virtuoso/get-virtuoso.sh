#!/bin/bash

# exit on error
set -e

VERSION=7.2.2
DEST_TGZ="virtuoso-opensource-${VERSION}.tar.gz"
DEST_TGZ_SHA1SUM="2afd8985e91416cc1ec64c67ac388ae30b4e4c4a  $DEST"
DEST_DIR="virtuoso-opensource-${VERSION}"
CORES="$(cat /proc/cpuinfo | grep ^processor | wc -l)"
PREFIX="$(pwd)/virtuoso-install"
URL="http://downloads.sourceforge.net/project/virtuoso/virtuoso/$VERSION/virtuoso-opensource-${VERSION}.tar.gz"

if [ '(' -z "$CORES" ')' -o '(' "$CORES" -lt 1 ')' ]; then
    echo "Couldn't detect number of cores, setting to 1"
    CORES=1
else
    echo "Detected $CORES cores"
fi

if [ ! -d "$PREFIX" ]; then
    if [ ! -d "$DEST_DIR" ]; then
        echo "Calculating checksum for $DEST_TGZ"
        if echo "$DEST_TGZ_SHA1SUM" | sha1sum -c -; then
            echo "$DEST_TGZ exists, and checksum is fine, skipping download"
        else
            echo "Re-downloading to $DEST_TGZ"
            wget -O "$DEST_TGZ" "$URL"
        fi

        tar xf "$DEST_TGZ"
    else
        echo "$DEST_DIR already exists; no need to unpack"
    fi

    echo "Configuring Virtuoso"
    pushd "$DEST_DIR"
    ./configure --prefix "$PREFIX"
    popd
    echo "Building virtuoso with $CORES threads"
    make -j$CORES -C "$DEST_DIR"
    echo "Installing to $PREFIX"
    make -j$CORES -C "$DEST_DIR" install
else
    echo "$PREFIX already exists; there is nothing to do"
fi
