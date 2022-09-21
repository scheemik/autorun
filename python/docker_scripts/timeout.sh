#!/bin/bash

pid=$1
repeat=$2
timer=$3
filename=$4

#Try sleeping for timer length, repeat number of times.
#if we get to the end of the timer x repeat, kill it.
count=0
for i in `seq 1 $repeat` ; do 
    echo -n "."
    kill -s 0 $pid >/dev/null 2>&1
    running=$?
    if [[ $running -ne 0 ]] ; then
        echo "$filename finished running after " $((count*$timer)) " seconds"
        break
    fi
    count=$((count+1))
    sleep $timer
done

kill -s 0 $pid >/dev/null 2>&1
running=$?
if [[ $running -eq 0 ]] ; then
	echo "Timeout for $filename"
	kill -9 $pid
fi

