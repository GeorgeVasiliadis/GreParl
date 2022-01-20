import io
from typing import Callable
from ..backend.speech import Speech
from ..backend.speech_file import SpeechFile
from collections import defaultdict
import os


def party(speech: Speech):
    """
    Get the speaker name
    :param speech:
    :return:
    """
    return speech.political_party


def speaker_name(speech: Speech):
    return speech.member_name


def create_groups(speech_file: SpeechFile, attributes: list[Callable[[Speech], str]], replace=False):
    """
    Read all speeches from the speeches file and group them using the functions in the attributes list.
    Each function accepts a Speech as input and returns a string. A file is created for every attribute.
    Each file contains
    :param speech_file Speech file
    :param attributes: list of callable objects extracting an attribute from each speech.
    :param replace: Delete existing group files
    """
    # For each attribute create a dictionary.
    # In every attribute dictionary map each value of the attribute to a list of the document ids with that attribute
    # For example: attribute_map = {speaker_name: {
    #                                 'Γιώργος Παπανδρέου': [1,2,3],
    #                                 'Αντώνης Σαμαράς': [4,5,6]
    #                                },
    #                               'party': {
    #                                 'ΠΑΣΟΚ': [1,2,3],
    #                                 ...
    #                                }
    #                                ...
    #                              }
    attribute_map = {}
    for attribute in attributes:
        attribute_map[attribute] = defaultdict(list)
    for speech_id, speech in enumerate(speech_file.speeches()):
        # For each attribute
        for attribute in attributes:
            # Get the dict with the values of the current attribute
            current_attribute = attribute_map[attribute]
            # Get the attribute value from the current speech.
            current_value = attribute(speech)
            # Skip speeches with no values?
            # if current_value == "":
            #     continue
            # Add the speech id to the list of the given value
            current_attribute[current_value].append(speech_id)
    # Write the group files
    for attribute in attributes:
        attribute_name = attribute.__name__
        if not replace and os.path.exists("groups/{}".format(attribute_name)):
            raise RuntimeError("File groups/{} already exists and replace is not specified.".format(attribute_name))
        current_attribute = attribute_map[attribute]
        with open("groups/{}".format(attribute_name), "w", encoding="utf8") as attribute_file:
            for attribute_value, document_ids in current_attribute.items():
                attribute_file.write(attribute_value)
                attribute_file.write(",")
                attribute_file.write(",".join([str(doc_id) for doc_id in document_ids]))
                attribute_file.write("\n")
            # Delete the last newline
            attribute_file.seek(-1, io.SEEK_END)
            attribute_file.truncate()
