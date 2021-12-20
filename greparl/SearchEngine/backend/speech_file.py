from ..preprocessing.funcs import process_csv_line


class SpeechFile:

    def __init__(self, speeches_csv_name):
        self.speeches_file = open(speeches_csv_name, "r", encoding='utf8')
        # Dict matching the ID of each speech (line number - 1 as first line contains explanations) to its offset
        # in the speeches file.
        self.speeches_offset = {}
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

    def get_speech(self, speech_id: int):
        # Find the nearest offset in the offsets array
        offset = self.speeches_offset[speech_id//100]
        # Read the line at the offset
        self.speeches_file.seek(offset)
        line = self.speeches_file.readline()
        # Read remaining lines and get to the requested one
        for i in range(speech_id % 100):
            line = self.speeches_file.readline()
        speech = process_csv_line(line)
        speech.id = speech_id
        return speech
