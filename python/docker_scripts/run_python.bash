#!/bin/bash


function now()
{
	echo `date +"%Y/%m/%d %H:%M:%S"`
}

function ctime()
{
	echo "-+-" $(now) ": "
}


echo $(ctime) "Changing to python directory"

for dir in /submission/sub ; do
    if [ ! -d $dir ] ; then
	continue
    fi

    cd $dir
    for filename in *.py
    do
        echo
    	echo "=============START $filename==================="
    	echo $(ctime) "Running " $filename
        #style
    	pycodestyle -qq --statistics $filename
    
    	n=`date +"%Y%m%d%H%M%S"`
    	echo $(ctime) "Running " $filename
	export MPLBACKEND=Agg
    	python $filename & # > ../logs/$filename.$n.out 2>../logs/$filename.$n.err & #fork
    	PID=$!
    	../scripts/timeout.sh $PID 1 1800 $filename 2> ../logs/$filename.$n.timeout.err > ../logs/$filename.$n.timeout.out &
    	SLEEP_PID=$!
    	wait $PID > /dev/null 2>&1
    	err=$?
    	if [[ $err -eq 0 ]] ; then 
        # commandThatMayHand.sh did not hang, fine, no need to monitor it anymore
        	echo $(ctime) "File $filename finished"
    	else
    		echo $(ctime) "File $filename finished with error $err"
    	fi
    	kill -s 0 $pid >/dev/null 2>&1
    	running=$?
    	if [[ $running -eq 0 ]] ; then
        	kill -9 $SLEEP_PID 2> /dev/null 2>&1
    	fi
    	echo "=============END $filename==================="

    done

done