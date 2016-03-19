#!/bin/bash

function run() {
    cd $1
    echo RUNNING $1
    ./run-$1.sh 1> stdout.log 2> errors.log
}

run fuseki &
run elda

