from os import listdir,chdir
from typing import TextIO, Dict


def _get_group_file_contents(group_file: TextIO) -> Dict[str, list[int]]:
    """
    Get a dictionary from a group file.
    """
    group_file.seek(0)
    groups = {}
    while line := group_file.readline():
        contents = line.split(",")
        groups[contents[0]] = [int(i) for i in contents[1:]]
    return groups


class GroupManager:
    """
    Class responsible for opening and parsing group files
    """

    def __init__(self, group_directory="groups"):
        # Dict containing another dict for each attribute that we have grouped by
        self.groups = dict()
        # Get all files in groups subdirectory
        group_files = listdir(group_directory)
        for file_name in group_files:
            with open("{}/{}".format(group_directory, file_name), "r", encoding="utf8") as file:
                self.groups[file_name] = _get_group_file_contents(file)

    def get_group_attributes(self) -> set[str]:
        return set(self.groups.keys())

    def get_attribute(self, attribute: str) -> Dict[str, list[int]]:
        """
        Get the dictionary for the given attribute mapping each value to a list of document ids.
        """
        if attribute not in self.groups.keys():
            raise RuntimeError("No groups available for attribute {}. Available groups {}"
                               .format(attribute, ",".join(self.groups.keys())))
        return self.groups[attribute]
