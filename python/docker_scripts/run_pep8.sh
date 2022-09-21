#!/bin/bash


function now()
{
    echo `date +"%Y/%m/%d %H:%M:%S"`
}

function ctime()
{
    echo $(now) ": "
}


echo $(ctime) "Changing to python directory"
cd /submission/py
ls
for filename in *.py
do
    n=`date +"%Y%m%d%H%M%S"`
    echo $(ctime) "Processing " $filename
    python $filename > ../logs/$filename.$n.out 2>../logs/$filename.$n.err & #fork
    PID=$!
    ../scripts/timeout.sh $PID 60 $filename 2> ../logs/$filename.$n.timeout.err > ../logs/$filename.$n.timeout.out &
    SLEEP_PID=$!
    wait $PID > /dev/null 2>&1
    err=$?
    if [[ $err -eq 0 ]] ; then 
    # commandThatMayHand.sh did not hang, fine, no need to monitor it anymore
        kill -9 $SLEEP_PID 2> /dev/null 2>&1
        echo $(ctime) "File $filename finished without error"
    else
        echo $(ctime) "File $filename finished with error $err"
    fi
done