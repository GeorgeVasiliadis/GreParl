from .inverted.inverted_index import InvertedIndex
from .speech import Speech
from .speech_file import SpeechFile
from ..preprocessing.funcs import process_raw_speech_text


class SpeechBackend:

    def __init__(self, index_file="index/index", speeches_file="speeches.csv"):
        self.index = InvertedIndex(index_file)
        self.speeches_file = SpeechFile(speeches_file)

    def search(self, query: str, number_of_results = 10) -> list[Speech]:
        processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=True)
        # Check if query only has stopwords
        if len(processed_query) == 0:
            processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=False)
        document_ids = self.index.search(processed_query, number_of_results=number_of_results)
        return [self.speeches_file.get_speech(document_id) for document_id in document_ids]
