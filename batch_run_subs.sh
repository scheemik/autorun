#!/bin/bash

# Make sure conda environment is activated (phy407)

LAB=Lab01

# Process all submissions in provided directory
for file in submission/$LAB/*
do
	[ -d "$file" ] || continue # Only consider directories
	FILENAME=${file##*/}
	./process_submission.bash $LAB/$FILENAME
done
