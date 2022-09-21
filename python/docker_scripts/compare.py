#!/usr/bin/env python
from subprocess import call
import sys
import os
from pycode_similar import *

def compare(reference_files, test_files, percentage=70, linecount=50):
    def get_file(value):
        r = open(value, 'rb')
        return (r.name, r.read())

    
    reference = [get_file(v) for v in reference_files]
    test = [get_file(v) for v in test_files]

    import itertools
    from tqdm import tqdm
    all_results = []
    for pair in tqdm(itertools.product(reference, test), total=len(reference)*len(test)):
        try:
            results = detect([c[1] for c in pair])
        except NoFuncException as ex:
#            print('error: can not find functions from {}.'.format(pair[ex.source][0]))
            continue
        except (SyntaxError,ValueError) as ex:
            continue

        for index, func_ast_diff_list in results:
            sum_total_count = sum(func_diff_info.total_count for func_diff_info in func_ast_diff_list)
            sum_plagiarism_count = sum(func_diff_info.plagiarism_count for func_diff_info in func_ast_diff_list)
            all_results.append([sum_plagiarism_count / float(sum_total_count) * 100,
                            sum_plagiarism_count,
                            sum_total_count,
                            pair[0][0], pair[1][0]])
#            if 100*(sum_plagiarism_count / float(sum_total_count)) > percentage and sum_total_count > linecount:
#                print("------------------")
#                print('ref: {}'.format(pair[0][0]))
#                print('candidate: {}'.format(pair[index][0]))
#                print('{:.2f} % ({}/{}) of ref code structure is plagiarized by candidate.'.format(
#                        sum_plagiarism_count / float(sum_total_count) * 100,
#                        sum_plagiarism_count,
#                        sum_total_count))

    return all_results
#        print('candidate function plagiarism details (AST lines >= {} and plagiarism percentage >= {}):'.format(
#            args.l,
#            args.p,
#        ))
#        output_count = 0
#        for func_diff_info in func_ast_diff_list:
#            if len(func_diff_info.info_ref.func_ast_lines) >= args.l and func_diff_info.plagiarism_percent >= args.p:
#                output_count = output_count + 1
#                print(func_diff_info)
#        if output_count == 0:
#            print('<empty results>')
#

def print_results(results, output):
    with open(output,'w') as handle:
        for p, pc, tc, ref, name in sorted(results)[::-1]:
            handle.write("{},{},{},{},{}\n".format(p,pc,tc,ref,name))
            if p > 80 and pc > 50:
                print(p, ref, name)


def find_target_files(directory, partner=""):
    results=[]
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            if name.endswith(".py") and "Partners_{}".format(partner) in root:
                results.append(os.path.join(root, name))
    return sorted(results)

def find_ref_files(directory):
    results=[]
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            if name.endswith(".py"):
                results.append(os.path.join(root, name))
    return sorted(results)


def main(reference, test, output):
    refdir = find_ref_files(reference)
    testdir = find_ref_files(test)
    print("ref: ", len(refdir))
    print("test: ", len(testdir))
    results = compare(refdir, testdir,70,50)
    print_results(results,output)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
