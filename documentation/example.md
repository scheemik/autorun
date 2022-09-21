# Example

## Downloading all assingment submissions

```python
./python/cli.py assignment download-submissions "Lab 2"
```

Output from the command

```
Lab 2 1730
Found  Lab 2 1730 2020-01-13 09:59:08.750733
Identity : 189911-1730
-> submission/Lab_2/Partners_12/sub/Lab02_Answer.pdf
-> submission/Lab_2/Partners_12/sub/function_lab02.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q1_b.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q1_c.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q1_d.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q2_a.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q2_b.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q2_c.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q2_d.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q3_b.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q3_c.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q4_a.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q4_b.py
Lab 2 4113
Found  Lab 2 4113 2020-01-13 09:59:24.867531
Identity : 189911-4113
-> submission/Lab_2/Partners_11/sub/Lab2+Report.pdf
-> submission/Lab_2/Partners_11/sub/Lab02_Q1b.py
-> submission/Lab_2/Partners_11/sub/Lab02_Q1c%2Cd.py
-> submission/Lab_2/Partners_11/sub/Lab02_Q2.py
-> submission/Lab_2/Partners_11/sub/Lab02_Q3.py
-> submission/Lab_2/Partners_11/sub/Lab02_Q4.py
Lab 2 5481
Found  Lab 2 5481 2020-01-13 09:59:29.358404
Identity : 189911-5481
-> submission/Lab_2/Partners_49/sub/Lab_2_Q1.py
-> submission/Lab_2/Partners_49/sub/Lab_2_Q2.py
-> submission/Lab_2/Partners_49/sub/Lab_2_Q3.py
-> submission/Lab_2/Partners_49/sub/Lab_2_Q4.py
```

For each submission that is checked, the Lab name and group ID is printed. 
```Lab 2 1730```

Followed by log entry to say that a submission is found
```Found  Lab 2 1730 2020-01-13 09:59:08.750733```

Followed by a unique ID for the lab/submission (from the quercus internal IDs)
```Identity : 189911-1730```

Followed by a list of files in the submission, yellow if they are new to the program, green if they have been downloaded already.
```
-> submission/Lab_2/Partners_12/sub/Lab02_Answer.pdf
-> submission/Lab_2/Partners_12/sub/function_lab02.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q1_b.py
-> submission/Lab_2/Partners_12/sub/Lab02_Q1_c.py
```

## Running a single assignment

./process_submission.sh "Lab_name/User_name"

