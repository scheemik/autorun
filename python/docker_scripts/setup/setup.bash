#!/bin/bash
for dir in py ipynb_converted_py sub
do
  if [ -d $dir ] ; then
      cp scripts/setup/*.bash $dir
  fi
done