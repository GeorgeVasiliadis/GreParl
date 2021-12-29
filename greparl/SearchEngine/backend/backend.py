import pickle

from .inverted.inverted_index import InvertedIndex
from .speech import Speech
from .speech_file import SpeechFile
from .top.get_top_words import KeywordManager
from ..preprocessing.funcs import process_raw_speech_text
from .top.group_manager import GroupManager
from datetime import date


class SpeechBackend:

    def __init__(self, index_file="index", speeches_file="speeches.csv"):
        self.speeches_file = SpeechFile(speeches_file)
        self.index = InvertedIndex(index_file)
        self.group_manager = GroupManager()
        self.keyword_manager = self._get_keyword_manager()

    def _get_keyword_manager(self) -> KeywordManager:
        vectorizer = pickle.load(open("tfidf/vectorizer.pkl", "rb"))
        transformer = pickle.load(open("tfidf/transformer.pkl", "rb"))
        return KeywordManager(vectorizer, transformer)

    def search(self, query: str, number_of_results=10) -> list[Speech]:
        processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=True)
        # Check if query only has stopwords
        if len(processed_query) == 0:
            processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=False)
        document_ids = self.index.search(processed_query, number_of_results=number_of_results)
        return [self.speeches_file.get_speech(document_id) for document_id in document_ids]

    def get_available_attributes(self) -> set[str]:
        """
        Get all the attributes the speeches have been grouped by.
        """
        return self.group_manager.get_group_attributes()

    def get_attribute_values(self, attribute: str) -> set[str]:
        """
        Get all values for a given attribute
        """
        return set(self.group_manager.get_attribute(attribute).keys())

    def get_keywords(self, attribute: str, attribute_value: str, period_start: date, period_end: date,
                     k=50, custom_stopwords=None) -> list[str]:
        """
        Get the keywords for documents with the given attribute value in the given time period.
        :param k number of keywords to fetch
        :param custom_stopwords set of words that will be ignored in keyword extraction
        :return: ordered list of keywords
        """
        # Get all the documents with the given attribute value
        speech_ids = self.group_manager.get_attribute(attribute)[attribute_value]
        # Get all the documents in the group from the file
        speeches = self.speeches_file.get_speeches(speech_ids)
        # Keep only the documents in the specified date range
        speeches = [speech.contents for speech in speeches if period_start <= speech.sitting_date <= period_end]
        keywords = self.keyword_manager.get_keywords(".".join(speeches), k=k, custom_stopwords=custom_stopwords)
        return keywords
