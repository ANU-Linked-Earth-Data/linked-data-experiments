#!/bin/bash

function run() {
    cd $1
    ./run-$1.sh >> log
}

run fuseki &
run elda

