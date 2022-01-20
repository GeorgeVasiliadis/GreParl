import gzip
import pickle
import typing

from .inverted.inverted_index import InvertedIndex
from .lsa.lsa_manager import LSAManager
from .similarity.similarity_manager import SimilarityMember, SimilarityManager, SimilarityResult
from .speech import Speech
from .speech_file import SpeechFile
from .top.keyword_manager import KeywordManager
from ..preprocessing.funcs import process_raw_speech_text
from .top.group_manager import GroupManager
from datetime import date


class SpeechBackend:

    def __init__(self, index_file="index", speeches_file="speeches.csv"):
        self.speeches_file = SpeechFile(speeches_file)
        self.index = InvertedIndex(index_file)
        self.group_manager = GroupManager()
        self.keyword_manager = self._get_keyword_manager()
        self.similarity_manager = SimilarityManager()
        self.lsa_manager = LSAManager()
        self.model_file = self._get_model_file()

    def _get_model_file(self):
        return gzip.open("models/party", "rb")

    def _get_keyword_manager(self) -> KeywordManager:
        vectorizer = pickle.load(open("tfidf/vectorizer.pkl", "rb"))
        transformer = pickle.load(open("tfidf/transformer.pkl", "rb"))
        return KeywordManager(vectorizer, transformer)

    def _initialize_dates(self):
        self.start_date = self.speeches_file.total_speeches

    def search(self, query: str, number_of_results=10) -> list[Speech]:
        processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=True)
        # Check if query only has stopwords
        if len(processed_query) == 0:
            processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=False)
        document_ids = self.index.search(processed_query, number_of_results=number_of_results)
        speeches = self.speeches_file.get_speeches(document_ids, preserve_order=True)
        return speeches

    def search_lsa(self, query: str, number_of_results=10) -> list[Speech]:
        """
        Search using LSA
        :param query: query string
        :param number_of_results: number of results to fetch
        :return: list of
        """
        processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=True)
        # Check if query only has stopwords
        if len(processed_query) == 0:
            processed_query = process_raw_speech_text(query, perform_stemming=True, delete_stopwords=False)
        document_ids = self.lsa_manager.search(processed_query, k=number_of_results)
        speeches = self.speeches_file.get_speeches(document_ids, preserve_order=True)
        return speeches

    def get_speech(self, speech_id: int) -> Speech:
        """
        Get the speech with the given id
        :raises RuntimeError if speech does not exist
        """
        return self.speeches_file.get_speech(speech_id)

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
        :param attribute if 'speech' get keywords for only one speech, otherwise get keywords for the given
                        attribute groups
        :param attribute_value if the attribute is 'speech' should be a speech id, otherwise an attribute value
        :param k number of keywords to fetch
        :param custom_stopwords set of words that will be ignored in keyword extraction
        :return: ordered list of keywords
        """
        # Get all the documents with the given attribute value
        if attribute != 'speech':
            speech_ids = self.group_manager.get_attribute(attribute)[attribute_value]
            # Get all the documents in the group from the file
            speeches = self.speeches_file.get_speeches(speech_ids, preserve_order=False)
            # Keep only the documents in the specified date range
            speeches = [speech.contents for speech in speeches if period_start <= speech.sitting_date <= period_end]
        else:
            # Get keywords for single speech
            speech_ids = int(attribute_value)
            speeches = [self.speeches_file.get_speech(speech_ids).contents]
        # Join all the speeches of the group into one big speech.
        keywords = self.keyword_manager.get_keywords(".".join(speeches), k=k, custom_stopwords=custom_stopwords)
        return keywords

    def get_most_similar(self, k=50) -> list[tuple[SimilarityMember, SimilarityMember, float]]:
        """
        Get the most similar parliament member pairs.
        :param k: Number of pairs to get
        :return: List with tuples. Each tuple contains: Two SimilarityMember object corresponding to the two members.
                 Their similarity score [0-1].
        """
        return self.similarity_manager.get_most_similar(k=k)

    def get_most_similar_to(self, member_name: str, k=10) -> SimilarityResult:
        """
        Returns the k members most similar to the given member.
        :return: SimilarityResult object. See its docs.
        """
        return self.similarity_manager.get_most_similar_to(member_name, k=k)

    def get_similarity_between_members(self, member1_name: str, member2_name: str) -> SimilarityResult:
        """
        Returns the similarity between the given two members.
        :return: SimilarityResult with the given member and one other member.
        """
        return self.similarity_manager.get_similarity_between_members(member1_name, member2_name)

    def predict_party(self, text: str) -> list[str]:
        """
        Try to predict the member of which party said the given text.
        :param text: Text to try to predict
        :return: Which party's member could have said the text.
        """
        # Process the given text
        processed_text = process_raw_speech_text(text)
        # Use the LSA vectorizer to extract the TF-IDF values
        vectorizer = pickle.load(open("lsa/vectorizer.pkl", "rb"))
        processed_text = vectorizer.transform([" ".join(processed_text)])
        self.model_file.seek(0)
        model = pickle.load(self.model_file)
        return model.predict(processed_text)


    def get_date_range(self) -> tuple[date]:
        """
        Get the dates of the oldest and newest speeches.
        :return: tuple containing the date of the oldest speech and the date of the newest speech in the file.
        """
        return self.speeches_file.date_range

    def get_total_speeches(self) -> int:
        return self.speeches_file.total_speeches
