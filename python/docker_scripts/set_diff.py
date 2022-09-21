#!/usr/bin/env python
import sys

if __name__=="__main__":
    before, after, new = sys.argv[1:]
    f_before = set(s.strip() for s in open(before).readlines())
    f_after = set(s.strip() for s in open(after).readlines())

    f_new = f_after - f_before
    with open(new,'w') as h:
        for f in f_new:
            h.write(f+"\n")
    