#!/bin/bash

function run() {
    cd $1
    echo RUNNING $1
    ./run-$1.sh 1>> ../log 2>> ../log
}

run fuseki &
run elda &

tail -f log

