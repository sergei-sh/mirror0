#!/bin/bash
for F in $(cat hide_list); do
    rm -f /home/serj/work/release/$F
    NOPY=${F%.py}
    echo $NOPY
    cp /home/serj/work/mirror0/build/lib.linux-x86_64-2.7/$NOPY.so /home/serj/work/release/$F
done