#!/bin/bash

# Make sure conda environment is activated (phy407)

LAB=Lab07

# Make sure there is a submission folder for that lab
if [ -d submission/$LAB ]
then
	continue
else
	echo "No directory for $LAB, aborting script"
	exit 1
fi

# Change to the correct directory
cd submission/$LAB

# Process all submissions in provided directory
for file in ./*
do
	# Replace any spaces with underscores to avoid problems later
	TEMP=${file#*/}
	file2=${TEMP// /_}
	# file2=${file// /_}
	mv "$file" "$file2"
	# Check whether $file is a directory or not
	if [ -f $file2 ]
	then
		# Find which lab group this file belongs to based on name
		TEMP=${file2%%_*}  # cut the string at the first underscore, keep before
		#		Expecting a name like "lab06group7_1234567_7654321_Lab06_Q2a.py"
		if [[ $file2 == lab* ]]
		then
			GROUP=${TEMP#*p}  # cut the string at the first `p`, keep after
		else
			GROUP=${TEMP}
		fi
		# Check to see whether a folder exists for that group
		GROUP_DIR=${LAB}_groups_${GROUP}
		if [ -d $GROUP_DIR ]
		then
			echo "Yay"
		else
			mkdir $GROUP_DIR
			mkdir $GROUP_DIR/sub
		fi
		# Remove the beginning of the file name to leave them just with the file
		#		name that the students submitted them with. This is important to make
		#		sure import statements across their scripts work correctly
		TEMP1="${file2#*_}"
		TEMP2="${TEMP1#*_}"
		F_NAME="${TEMP2#*_}"
		# # Move that file to the appropriate directory
		mv $file2 $GROUP_DIR/sub/$F_NAME
	fi
done
