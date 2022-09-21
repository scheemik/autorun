#!/bin/bash

#find the ipynb files in the ipynb directory.

cd /submission/
cd sub
for filename in *.ipynb
do
        bname=`basename $filename`
	echo "Processing " $filename

	if [ ! -e ../ipynb_converted_py ] ; then
	    mkdir ../ipynb_converted_py
	fi
	jupyter nbconvert --to python $filename --output-dir ../ipynb_converted_py > ../logs/$bname.topy.out 2> ../logs/$bname.topy.err

	if [ ! -e ../ipynb_converted_pdf ] ; then
	    mkdir ../ipynb_converted_pdf
	fi
	jupyter nbconvert --to pdf $filename --output-dir ../ipynb_converted_pdf > ../logs/$bname.topdf.out 2> ../logs/$bname.topdf.err
	
done

