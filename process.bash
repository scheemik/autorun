#!/bin/bash

#This script runs a single lab submission by converting 
#all of the notebooks to python, then running the code.
#saving the output and any figures generated

#1. Setup the directory names
prefix=$1
lab_name=$2
lab=`echo $lab_name | tr " " "_"`
full_lab=$prefix/$sane_lab
echo $prefix $lab_name #$full_lab
setup_script=$3
run_name=`echo $lab_name | tr "/," "__"`
base_run=`dirname $lab_name`
#This entry needs to change to the location of your 
#source material for code checking.
SOLUTION_REPOSITORIES=`pwd`/possible_sources

function now()
{
	#today's date and time
	echo `date +"%Y/%m/%d %H:%M:%S"`
}

function ctime()
{
	#printing out a separator in the log file.
	echo "-+-" $(now) ": "
}

#2. Start of the log file
echo $(ctime) "-------------------- START $lab"

#3. Make a directory for the assignment
if [ ! -d $prefix/run/$base_run ] ; then
    mkdir -p $prefix/run/$base_run
fi

if [ -e $prefix/run/$lab ] ; then
	echo $(ctime) "Already run $lab"
else
#Inside the else we haven't run this lab yet.
#All the way to the last line of the file
	if [ ! -d $full_lab ] ; then
		echo $(ctime) "Directory $full_lab doesn't exist!"
		exit 1
	fi
#4. log the date and time
	date > $prefix/run/$lab
	echo $(ctime) "Processing $lab"
	echo $(ctime) "Copying support files"

#5. Copy some support scripts to the user directory
#TODO symbolic link should work? maybe not on dropbox.
	mkdir $prefix/$lab/scripts
#6. copy the docker support scripts into the right location
#TODO move the scripts to the source directory
	cp -R python/docker_scripts/* $prefix/$lab/scripts
#7. list the scripts into the log file for debugging
	ls $prefix/$lab/scripts

	cd $prefix/$lab
	pwd
#Now we are	inside the users submission
#There should be a 'sub' directory containing the raw submission
#and a logs directory containing the logs

#8. empty the log directory
	if [ -d logs ] ; then
		rm -rf logs
	fi
	mkdir logs

#9. report on the files we're about to use
	for ext in ipynb pdf py; do 
		echo $(ctime) "Found the following $ext files"
			for f in `find . -mindepth 1 -name "*.$ext"` ; do
				echo -e "\t $f"
			done
	done

#10. If there are ipynb notebook files. Run a docker instance to 
#convert them to Python using a script and 
#save that converted for running later.
#TODO run the notebook directory to protect against ipython magic usage.
	find . -name "[pi]*" -type f > logs/T_files_before.list
	ls sub/*.ipynb >/dev/null 2>&1
	if [ $? -eq 0 ] ; then
		echo $(ctime) "Converting Notebooks and converting PDF"
		ls sub/*.ipynb
		docker run --rm -v `pwd`:/submission \
			   --name=convert_$run_name\
			   -t autorun\
			   /submission/scripts/convert_ipynb_to_py.bash > logs/docker.convert.run.out 2>logs/docker.convert.run.err
#	    docker rm convert_$run_name
#10b. Now that we have the python code. Run the code comparison
#to check for copies.
	if [ -d $SOLUTION_REPOSITORIES ] ; then
		echo $(ctime) "---start comparing notebook code---"
	    ./scripts/compare.py $SOLUTION_REPOSITORIES ./ipynb_converted_py logs/PCipynb.out
	    echo $(ctime) "---end comparing notebook code---"
	fi

	else
		echo $(ctime) "No Notebooks found"
	fi
#10c. Log the file changes before and after running this code. To check for changes.
	find . -name "[pi]*" -type f > logs/T_files_after.list	
	scripts/set_diff.py logs/T_files_before.list logs/T_files_after.list logs/new_converted_files.list
	rm logs/T_*.list

#11. If there are python files. Run all of one with a docker instance.
	find . -name "[pi]*" -type f > logs/T_files_before.list
	ls sub/*.py &>/dev/null
	if [ $? -eq 0 ] ; then
#11b. If there is a setup script for this lab. Run it (usually copying data into the directory)
		echo $(ctime) "Running Python"
	    if [ ! -z $setup_script ] ; then
	        if [ -e scripts/$setup_script ] ; then
	        	echo $(ctime) "Running $setup_script"
				scripts/$setup_script 
			else
				echo $(ctime) "ERROR : $setup_script not found"
			fi

	    else
	        echo $(ctime) "Not running setup script"
	    fi
	    echo $(ctime) "Starting docker run_$run_name"
		docker run --rm -v `pwd`:/submission \
			   --name=run_$run_name\
			   -t autorun\
			   /submission/scripts/run_python.bash > logs/docker.python.run.out 2>logs/docker.python.run.err
#	    docker rm run_$run_name
	    if [ -d $SOLUTION_REPOSITORIES ] ; then
	    	echo $(ctime) "---start comparing python code---"
		    ./scripts/compare.py $SOLUTION_REPOSITORIES ./sub logs/PCipynb.out
		    echo $(ctime) "---end comparing python code---"
		fi
	else
		echo $(ctime) "No Python files found"
	fi
#11c. Log the file changes before and after running this code. To check for changes.
	find . -name "[pi]*" -type f > logs/T_files_after.list	
	scripts/set_diff.py logs/T_files_before.list logs/T_files_after.list logs/new_exec_files.list
	rm logs/T_*.list
	
	######### END
	
#14. Concatenate all of the logs with separators into one file.
	find logs -size  0 -print0 |xargs -0 rm --
	echo $(ctime) "---- OUTPUT logs ----"
	for f in `find logs -name '*.out'` ; do
		echo $(ctime) "++++ " $f " ++++"
		cat $f
	done
	echo $(ctime) "---- ERROR logs ----"
	for f in `find logs -name '*.err'` ; do
		echo $(ctime) "++++ " $f " ++++"
		cat $f
	done

	echo $(ctime) "---- FILES logs ----"
	for f in `find logs -name '*.list'` ; do
		echo $(ctime) "++++ " $f " ++++"
		cat $f
	done

	#echo $(ctime) "---- pycodestyle logs ----"
	#for f in `find py -name '*.pycodestyle'` ; do
	#	echo $(ctime) "++++ " $f " ++++"
	#	cat $f
	#done
	
	echo $(ctime) "Cleaning up log files"
#15. Compress the raw scripts and logs into a tar file and remove them.
#TODO symbolic link of scripts might be easier.
#TODO but the student 'could' destroy the scripts directoy.
	tar cfz run_`date +%Y%m%d_%H%M`.tar.gz scripts logs
	rm -rf scripts logs
	cd -
fi

echo $(ctime) "-------------------- END $lab"
