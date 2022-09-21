#!/usr/bin/env python
"""Command line interface to Quercus to download submissions."""
import click
import json
import api
from datetime import datetime

def now():
    """Date and time in string form."""
    return datetime.strftime(datetime.now(),"%Y%m%d_%H%M%S")

@click.group()
def cli():
    """CLI."""
    pass


@cli.command()
def groups():
    """Get the group names"""
    current_course = api.CourseInstance()
    u = current_course.get_groups()
    print(u)


@cli.command()
@click.option("--filename", default="submission/data/users.csv")
@click.option("--force", default=False, is_flag=True)
def users(filename, force):
    """Get the user information and store in the user cache file submission/data/users.csv
    Args:
        None
    Options:
        filename : The filename to save to
        force : boolean to force reload (default is False)
    Returns:
        None
    Prints:
        The user names
    """
    current_course = api.CourseInstance()
    u = current_course.get_users(filename,force)
    print(u)


@cli.group()
def assignment():
    """Group
    """
    pass


@assignment.command()
@click.option("--filename", default="submission/data/assignments.csv")
@click.option("--force", default=False, is_flag=True)
def download(filename, force):
    """Download and assignment, DEPRECATED
    Options:
        filename : cache filename for assignments
    """
    current_course = api.CourseInstance()
    a = current_course.get_assignments(filename, force)


@assignment.command()
@click.argument("assignment_name")
def find(assignment_name):
    """Finds an assignment and prints the assignment ID.
    Args:
        assignment_name : The name of the assignment
    """
    current_course = api.CourseInstance()
    _assignment = current_course.find_assignments(assignment_name)
    print(_assignment)

@assignment.command('list')
@click.option("--filter",default=None)
def alist(filter):
    """Lists the assignments
    """
    current_course = api.CourseInstance()
    current_course.list_assignments(filter=filter)
    


@assignment.command()
@click.argument("assignment_name")
@click.option("--filter",default=None)
@click.option("--single",default=False, is_flag=True)
def find_submissions(assignment_name, filter, single):
    """Finds an assignment submission for this user
    Args:
        assignment_name : The name of the assignment
        filter : user name or id
    """
    current_course = api.CourseInstance()
    try:
        _assignment = current_course.find_assignments(assignment_name)
        if len(_assignment):
            current_course.find_submissions(_assignment.index[0],filter, single=single)
    finally:
        del current_course


@assignment.command()
@click.argument("assignment_name")
@click.option("--filter", default=None)
def download_submissions(assignment_name, filter):
    """Download the submissions for this assignment
    Args: 
        assignment_name : The name of the assignment to download
    Side effect:
        A lot of submissions files in the submission directory.
        Saves a json file of the files downloaded.
    """
    current_course = api.CourseInstance()

    s = current_course.download_submissions(assignment_name, user_id=filter)
    if len(s):
        import os
        log_path="submission/data/downloaded/"
        s_assignment_name = assignment_name.replace(" ","_")
        file_path=os.path.join(log_path,"{}.{}.json".format(s_assignment_name,now()))

        if not os.path.exists(log_path):
            print("making {}".format(log_path))
            os.makedirs(log_path)
        json.dump(s,
                  open(file_path, 'w'),
                  indent=2, sort_keys=True)


@assignment.command()
@click.argument("assignment_name")
@click.argument("user_id")
def download_submission(assignment_name, user_id):
    """Download the submissions for this assignment
    Args:
        assignment_name : The name of the assignment to download
        user_id : User id to download
    """
    current_course = api.CourseInstance()
    sub = current_course.download_submission(assignment_name, user_id, single=single)

if __name__ == "__main__":
    cli()