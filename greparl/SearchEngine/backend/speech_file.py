from collections import defaultdict

from .speech import Speech
from ..preprocessing.funcs import process_csv_line


class SpeechFile:

    def __init__(self, speeches_csv_name):
        self.speeches_file = open(speeches_csv_name, "r", encoding='utf8')
        # Dict matching the ID of every 100 speeches to its offset in the speeches file.
        self.speeches_offset = {}
        self.total_speeches = 0
        self.__calculate_offsets()

    def __calculate_offsets(self) -> None:
        """
        Adds the offsets of each speech to the speeches_offset dictionary. The speeches_offset dictionary matches
        the ID of each speech to its offset in the speeches file
        """
        self.speeches_file.seek(0)
        # Ignore the first line by starting document ids at -1. The first line is read but ignored, and the next line is
        # read and stored normally.
        document_id = -1
        # Read the next line before storing the offset to make sure there is one
        while self.speeches_file.readline():
            # Save document_id every 100 documents
            if document_id % 100 == 0:
                self.speeches_offset[document_id//100] = offset
            # Keep the offset of the new line before reading it
            if (document_id + 1) % 100 == 0:
                offset = self.speeches_file.tell()
            document_id += 1
        # Speech ids start at 0, so we add 1
        self.total_speeches = document_id + 1

    def get_speech(self, speech_id: int) -> Speech:
        """
        Gets a speech object given its ID
        :param speech_id:
        :return:
        """
        # Go to the offset of the nearest document stored in speeches_offset and then to the exact line the speech is
        # in.
        if speech_id > self.total_speeches - 1 or speech_id < 0:
            raise RuntimeError("Speech ID out of bounds. (Max speech ID: {}".format(self.total_speeches - 1))
        # Find the nearest offset in the offsets dict
        offset = self.speeches_offset[speech_id//100]
        # Read the line at the offset
        self.speeches_file.seek(offset)
        line = self.speeches_file.readline()
        # Read remaining lines and get to the requested one
        for i in range(speech_id % 100):
            line = self.speeches_file.readline()
        return process_csv_line(line)

    def get_speeches(self, speech_ids: list[int]) -> list[Speech]:
        """
        Gets the speeches with the given id from the file. Offers increased performance compared to individually getting
        each speech.
        :param speech_ids: list with ids of
        :return:
        """
        # Instead of going directly to the speeches, first group them and then read each bucket. This way each bucket
        # of 100 speeches is only read once.
        # Group speeches by their position in the offsets dict
        buckets = defaultdict(list)
        results = []
        for speech_id in speech_ids:
            buckets[speech_id//100].append(speech_id)
        for bucket, speeches in buckets.items():
            # Get the offset of the first speech in the bucket
            offset = self.speeches_offset[bucket]
            # Sort the speeches by their id
            speeches.sort()
            # Read the line at the offset and check if it is included in the desired speech IDs
            self.speeches_file.seek(offset)
            line = self.speeches_file.readline()
            if speeches[0] % 100 == 0:
                results.append(process_csv_line(line))
                speeches.pop(0)
            if len(speeches) > 0:
                for i in range(speeches[-1] % 100):
                    line = self.speeches_file.readline()
                    if bucket*100 + i + 1 == speeches[0]:
                        results.append(process_csv_line(line))
                        speeches.pop(0)
        return results

    def speeches(self):
        """
        Generator function iterating over the speeches of the file in order.
        Speech IDs start at 0, so to iterate over speeches with IDs use the enumerate function.
        :return: Speech object
        """
        self.speeches_file.seek(0)
        # Ignore the first line
        self.speeches_file.readline()
        while line := self.speeches_file.readline():
            yield process_csv_line(line)
