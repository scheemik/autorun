#!/bin/bash

#find the ipynb files in the ipynb directory.

cd /submission/

cd sub
for filename in *.ipynb
do
        bname=`basename $filename`
	echo "Processing " $filename
	if [ ! -e ipynb_converted_pdf ] ; then
	    mkdir ipynb_converted_pdf
	fi
	jupyter nbconvert --to pdf $filename --output-dir ../ipynb_converted_pdf > ../logs/$bname.topdf.out 2> ../logs/$bname.topdf.err

	echo "Running " $filename
	jupyter nbconvert --to python --execute $filename --output-dir ../ipynb_converted_pdf > ../logs/$bname.run.out 2> ../logs/$bname.run.err
done
