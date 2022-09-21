#!/bin/bash

#This code runs a downloaded lab submission using docker instances to
#protect the host computer. 

#Give the lab name and a setup script
#lab name is really a directory name underneath submission/

if [ -z $1 ] ; then
    echo "usage lab_name [setup_script]"
    exit
fi


prefix=submission
lab=$1
lab_run=`echo $lab | tr " " "_"`
full_lab=$prefix/$lab
setup=$2
base_run=`dirname $lab`
sane_lab=`echo $lab | tr " " "_"`
log_name=submission/logs/$sane_lab.out
err_name=submission/logs/$sane_lab.err

for dir in submission submission/logs submission/run
do
    if [ ! -d $dir ] ; then
        mkdir -p $dir
    fi
done


#Make the 'run' directory if needed, to log the fact that we ran the code
if [ ! -d submission/run/$base_run ] ; then
    mkdir -p submission/run/$base_run
fi


if [ ! -d submission/logs/$base_run ] ; then
    mkdir -p submission/logs/$base_run
fi
#echo $log_name
#echo $err_name

#Start logging to output and error files.
date > $log_name
date > $err_name

#Call the actuall processing code in the background
#./process.bash $prefix $lab $setup> $log_name 2> $err_name &
#echo $prefix/run/$lab_run
if [ -e $prefix/run/$lab_run ] ; then
    echo "Already run $lab"
else
    ./process.bash "$prefix" "$lab" "$setup" > $log_name 2> $err_name &
    

    # Now start the watcher with a 2 hour timer to kill it if it takes too long.
    PID=$!
    ./python/docker_scripts/timeout.sh $PID 1200 6 $lab
    SLEEP_PID=$!
    wait $PID #> /dev/null 2>&1
    err=$?
    if [[ $err -eq 0 ]] ; then 
        echo "Lab $lab finished"
    else
        echo "Lab $lab finished with error $err"
    fi
    
    
    kill -s 0 $SLEEP_PID >/dev/null 2>&1
    running=$?
    if [[ $running -eq 0 ]] ; then
        kill -9 $SLEEP_PID 2> /dev/null 2>&1
    fi
fi
