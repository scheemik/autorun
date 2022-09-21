"""Canvas/ Quercus API functions"""

from canvasapi import Canvas, requester
import dotenv
import os
import urllib.request
from tqdm import tqdm
import termcolor
import pandas as pd
import pickle
from datetime import datetime

import logging

test_student = 328809

class CourseInstance(object):
    """Instance to store the course information."""

    def __init__(self, config_file="python/q.key"):
        """Initialize the course with API keys"""

        # Find the config file, load it with dotenv
        filename = os.path.expanduser(config_file)
        dot = dotenv.load_dotenv(filename)
        api_key = os.getenv("API_KEY")
        api_url = os.getenv("API_URL")
        course_id = os.getenv("COURSE_ID")
        canvas = Canvas(api_url, api_key)
        course = canvas.get_course(course_id)

        self.course = course
        self.canvas = canvas
        self.load_sub_cache("_subs")
        return

    def __del__(self):
        try:
            self._subs = self._subs[["assignment", "user_id", "time"]]#, "user_name", "group_name"]]
            self.__save_cache("_subs", "submission/data/subs.csv")
        except Exception as e:
            print("Problem saving subs cache, {}".format(e))

    # To save on downloading data repeatedly from Canvas we
    # use caches stored in submission/data/subs.csv to store information on the
    # students, their submissions, etc.

    def __load_cache(self, attname, filename, force=False, index_col=0):
        """Loads a cache.

        Args:
            self : The class
            attname: The attribute name to save the cache to
            filename: The file to load as the cache
        Options:
            force: boolean to force reloading of the cache
            index_col: pandas annoyance about using index columns
        Returns:
            The cached data.
        """

        # If we have the attribute loaded and don't need to force a reload, return the attribute
        if hasattr(self, attname) and not force:
            return getattr(self, attname)

        # If the filename exists, load the file intro the attribute and return it.
        if filename is not None and os.path.exists(filename):
            setattr(self, attname, pd.read_csv(filename, index_col=index_col))
            return getattr(self, attname)

        return None

    def __save_cache(self, attname, filename):
        """Saves the attribute into the csv file.

        Args:
            attname : The attribute name to save
            filename : The csv file to save into
        Returns:
            The saved data
        """
        att = getattr(self, attname)
        if att is None:
            return None
        dname = os.path.dirname(filename)
        os.makedirs(dname, exist_ok=True)
        att.to_csv(filename)
        return

    def __get_data(self, generator, attributes, myattribute=None):
        """Get data from Quercus.

        Args:
            generator: The generator function if the data doesn't exist
            attributes: The attributes to retrieve from the generator and store
            in a dictionary.
        Options
            myattribute: If specified, where to save the attribute in the instance.
        Returns:
            The loaded data.
        """

        output_data = dict()
        input_data = generator()

        # Loop through the attributes and the generated data and store
        # each attribute from every element returned by the generator
        for k in attributes:
            output_data[k] = [getattr(one, k) for one in input_data]

        # Convert to a dataframe and set the index.
        output_data_df = pd.DataFrame(output_data).set_index("id")
        if myattribute is not None:
            setattr(self, myattribute, output_data_df)
        return output_data_df

    def get_data(self, generator, filename, fields, attname, force=False):
        """Get data from a cache, or Quercus.
        Args:
            generator : Generatoor function if the data doesn't exist.
            filename : Cache filename to (try to) load.
            fields : The fields to store from the generator
            attname : The cache name to save in the object.
        Options:
            force : boolean to force releoding of the data.
        Returns:
            The data.
        """
        if self.__load_cache(attname, filename, force) is None:
            # generate from canvas
            self.__get_data(generator, fields, attname)
            # save
            #print(attname, filename)
            self.__save_cache(attname, filename)
        return getattr(self, attname)

    def get_users(self, filename="submission/data/users.csv", force=False):
        """Get the user ids and sortable names.

        Options:
            filename : user cache filename, data/users.csv
            force : Force reload
        Returns:
            The user data
        """
        return self.get_data(
            self.course.get_users, filename, ["id", "sortable_name"], "_users", force
        )

    def get_groups(self, filename="submission/data/groups.csv", force=False):
        """Get the Group ids and names.

        Options:
            filename : group cache filename, data/groups.csv
            force : Force reload
        Returns:
            The group data
        """

        return self.get_data(
            self.course.get_groups, filename, ["id", "name"], "_groups", force
        )

    def get_assignments(self, filename="submission/data/assignments.csv", force=False):
        """Get the assignment ids and sortable names.

        Options:
            filename : assignment cache filename, submission/data/assignments.csv
            force : Force reload
        Returns:
            The assignment data
        """

        return self.get_data(
            self.course.get_assignments, filename, ["id", "name"], "_assignments", force
        )

    def load_sub_cache(self, attname, filename="submission/data/subs.csv", force=False):
        """Loads the submission cache.

        Args:
            attname : The attribute to save
        Options
            filename : The source cache file (submission/data/subs.csv)
            force : boolean to force reload.
        """
        # If the file doesn't exist, load from canvas.
        if self.__load_cache(attname, filename, force, index_col=None) is None:
            # generate from canvas
            setattr(
                self, attname, pd.DataFrame(columns=["assignment", "user_id", "time"])
            )
        return getattr(self, attname)

    def find_assignments(self, name):
        """Load the assignment list and return the id of an assignment with the matching name.

        Args:
            name : The assignment name
        Returns:
            The table entry containing the name and assignment id.
        """
        assignments = self.get_assignments()
        return assignments[assignments["name"] == name]

    def list_assignments(self, filter=None):
        for arow, assignment in self.get_assignments().iterrows():
            if filter is None:
                print(assignment["name"])
            elif filter in assignment["name"]:
                print(assignment["name"])

    def match_user(self, search, submission):
        found = False
        if search is None:
            return found

        user = self.get_user(mid=submission.user_id)
        if user is None:
            return found

        name = user.sortable_name
        try:
            if int(search) == sub.user_id:
                found = True
        except ValueError as e:
            if search in name:
                found = True
        return found

    def find_user(self, mid=None, name=None):
        """Find a user from the user id or name and return the table entry.

        If the user doesn't exist, return None
        Args:
            mid: user id
            name : user sortable name.
            (mid >> name in priority)
        Returns:
            Table entry from the user table or None
        """
        users = self.get_users()
        if mid is not None and mid!=test_student:
            return users[users.index == mid]
        elif name is not None:
            return users[users.sortable_name == name]
        else:
            return None

    def find_group(self, mid=None, name=None):
        """Find a grou from the grou id or name and return the table entry.

        If the group doesn't exist, return None
        Args:
            mid: group id
            name : group name
            (mid >> name in priority)
        Returns:
            Table entry from the group table or None
        """
        groups = self.get_groups()
        if mid is not None:
            return groups[groups.index == mid]
        elif name is not None:
            return groups[groups.name == name]
        else:
            return None

    def find_submissions(self, assignment_id, user_id, single=False):

        _assignment = self.course.get_assignment(assignment_id)
        found_user = False
        for sub in _assignment.get_submissions(include=["group"]):
            found=False
            if user_id is None:
                found = True
                found_user=True
            elif self.match_user(user_id, sub):
                found = True
                found_user=True

            if found:
                #get the submission
                data = self.process_submission(sub)
                def print_iter(key, iterable,tablen=0):
                    tabs= lambda x: "\t"*x
                    if isinstance(iterable,list):
                        print(tabs(tablen), key)
                        for it in iterable:
                            print(tabs(tablen+1),it)
                    elif isinstance(iterable,dict) and key=="attachments":
                        print(tabs(tablen), key)
                        for kit,it in iterable.items():
                            print(tabs(tablen+1),"->{}".format(it))
                    elif isinstance(iterable,dict):
                        print(tabs(tablen), key)
                        for kit,it in iterable.items():
                            print(tabs(tablen+1),"{}->{}".format(kit,it))
                    else:
                        print(tabs(tablen),"{}->{}".format(key,iterable))

                for key, val in data.items():
                    print_iter(key, val,1)
                    #termcolor.cprint("{} -> {}".format(key, val), "yellow")

                if single:
                    break
                else:
                    termcolor.cprint("-----------","yellow")

        if not found_user:
            termcolor.cprint("User {} not found".format(user_id), "red")




    def get_assignment(self, name):
        """Find the assignment id from its name,
        and get the assignment object from Quercus."""

        assignment = self.find_assignments(name)
        return self.course.get_assignment(assignment.index.values[0])

    def get_user(self, mid=None, name=None):
        """Find the user id from name (or id) and
         get the user object from Quercus."""

        user = self.find_user(mid, name)
        #logging.info("{}, {}".format(mid, name))
        # print("User: ", user.index, mid, name)
        if user is None:
            return None
        _user = self.course.get_user(user.index.values[0])
        return _user

    def get_group(self, mid=None, name=None):
        """Find the group id from name (or id) and
         get the group object from Quercus."""

        group = self.find_group(mid, name)
        return self.canvas.get_group(group.index.values[0])

    def process_submission(self, submission, ignore_list=None):
        """ Download the submission contents.
        Args:
            submission : The submission id
        Options:
            ignore_list :
        Returns:
        """

        # if self.sub_exist(assignment_name, submission.user_id):
        #    continue

        # Setup the data dictionary, save the submission time.
        data = dict()
        data["time"] = submission.submitted_at

        # If there is no submission (time) we're done.
        user = self.get_user(mid=submission.user_id)
        if user is None:
            return data
        data["user"] = user.sortable_name
        if data["user"] is None:
            return data

        if submission.submitted_at is None:
            return data

        # Save the group name and id if there a group.
        data["group"] = submission.group["name"]
        data["group_id"] = submission.group["id"]

        # Save the user name
        # Get the submitter id (can be different for groups)
        data["submitter_id"] = submission.user_id
        # Get whichever identity is better. Either the group or the user.
        identity = data["group"] or data["user"]

        # If there is an ignore list (i.e. for a repeat attempt), check it
        # and return if we found a duplicate.
        if ignore_list is not None and identity in ignore_list:
            return data

        # Save the identity.
        data["id"] = identity

        # We have a submission, if it's a gorup submission get all of the users
        # Otherwise just the user name.
        if data["group"] is not None:
            group_list = self.get_group(name=data["group"]).get_users()
            names = [user.sortable_name for user in group_list]
        else:
            names = data["user"]
        data["names"] = names

        # If there are attachments, save the location and
        # filename of the attachment for later downloading
        if hasattr(submission, "attachments"):
            data["attachments"] = dict(
                (att["url"], att["filename"]) for att in submission.attachments
            )
        # Return the captured information, but no downloaded files yet.
        return data



    def download_submissions(self, name, user_id=None):
        """Downloads all submissions to this assignment.

        Args:
            name : The assignment name.
            user_id : user id or name to filter for.
        Side effect :
            Downloaded files.
        """

        # Get the assigment object
        assignment = self.get_assignment(name)
        result = dict()
        # Get the submissions including a group name if there is one.
        subs = list(assignment.get_submissions(include=["group"]))
        # Loop through the submissions and download the contents.
        for submission in subs:
            found = False
            if user_id is None:
                found = True

            elif self.match_user(user_id, submission):
                found = True

            if found:
                identity, data = self.download_submission(
                    name, submission.user_id, result.keys()
                )
                # If 'time' is available (there is a submission),
                # save the submission information.
                if data["time"] is not None:
                    result[identity] = data
        # Return the submission information.
        return result

    def sub_exist(self, assignment_name, user_id, group_name, user_name):
        """Check if the submission exists.
        Args:
            assignment_name: The name of the assignment
            user_id : The user id
        Returns:
            boolean of the submission in the submission/data/subs.csv file.
        """

        # Check for an entry with the assignment and
        # user in the submission cache.
        exist = (
            sum(
                (self._subs["assignment"] == assignment_name)
                & (self._subs["user_id"] == user_id)
            )
            > 0
        )

        # Doesn't exist. Add to the cache
        if not exist:
            print("Found ", assignment_name, user_id, datetime.now())
            entry = dict(
                assignment=assignment_name,
                user_id=user_id,
                time=datetime.now(),
                user_name=user_name,
                group_name=group_name
            )
            self._subs = self._subs.append(entry, ignore_index=True)
            self.__save_cache("_subs", "submission/data/subs.csv")
        return exist

    def download_submission(
        self, assignment_name, user_id, ignore_list=None, parent_directory="submission"    ):
        """Download a single submission.
        Args:
            assignment_name : The assignment name
            user_id : The user id to download from
        Options
            ignore_list : A list of users already processed
            parent_directory: The location to save everything ,
                    parent_directory/assignment_name/group_user_name
        Returns:
            identity used and data entry
        Side Effect:
            Downloaded files.
        """

        print(assignment_name, user_id)

        # test student protection. Return if test
        if user_id == test_student:
            return None, dict(time=None)
        # If the submission exists, return
        #if self.sub_exist(assignment_name, user_id):
        #    return None, dict(time=None)

        # The submission is new at this point.
        # If the ignore list was None, make an empty list.
        ignore_list = ignore_list or []
        # Get the assignment and submission objects.
        assignment = self.get_assignment(assignment_name)
        submission = assignment.get_submission(user_id, include=["group"])


        # Save the submission time.
        data = dict()
        data["time"] = submission.submitted_at
        identity = None

        # Sanity check the directory name to remove spaces.
        pardir = os.path.join(parent_directory, assignment_name.replace(" ", "_"))

        # The submission time being None means there is a submission
        # Save the group name, id, user name, id and dominant identity.
        # This might be redundent if the information from process_submission is passed in.
        data["group"] = submission.group["name"]
        data["group_id"] = submission.group["id"]


        data["user"] = self.get_user(mid=submission.user_id).sortable_name
        data["id"] = submission.user_id
        identity = data["group"] or data["user"]
        print("Identity : {}".format(submission))
        if self.sub_exist(assignment_name, user_id, data["group"], data["user"]):
            return None, dict(time=None)

        if submission.submitted_at is not None:
            # We have a submission
            if data["group"] is not None:
                group_list = self.get_group(name=data["group"]).get_users()
                names = [user.sortable_name for user in group_list]
            else:
                names = data["user"]
            data["names"] = names

            # attachments
            # If there are attachments, save the location and
            # filename of the attachment for later downloading
            if hasattr(submission, "attachments"):
                data["attachments"] = dict(
                    (att["url"], att["filename"]) for att in submission.attachments
                    )
                # End of the almost redundent information.
                # Download the attachments for this submission.
                self.download_attachments(identity, data, pardir)
        # Return the id and the data object.
        return identity, data

    def download_attachments(self, identity, data, parent):
        """Downloads attachments from Quercus.
           Given the data dictionary, check for attachments and download
           each one if it doesn't exist already.

            Args:
                identity: The group/user id for the directory
                data : the dictionary containing files.
            Side effect:
                Downloaded files.
        """

        # Make a directory name and create the directory
        groupdir = os.path.join(parent, identity.replace(" ", "_"))
        os.makedirs(groupdir, exist_ok=True)

        # Loop throught the attachments, check for existing files,
        # Download new files.
        for url, filename in data["attachments"].items():
            ext = os.path.splitext(filename)[1][1:]

            # Make the submission directory
            path = os.path.join(groupdir, "sub")
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

            # Check for the file, download new files (yellow)
            dest = os.path.join(path, filename)
            if os.path.exists(dest):
                termcolor.cprint("-> " + dest, "green")
            else:
                termcolor.cprint("-> " + dest, "yellow")
                urllib.request.urlretrieve(url, dest)
