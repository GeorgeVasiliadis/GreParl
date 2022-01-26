from datetime import date

from .MockSpeech import mock_speech
from .MockSimilarity import MockSimilarityMember, MockSimilarityResult
from .MockSimilarity import mock_similarity_member, mock_similarity_result

# Type aliases
SimilarityMember = MockSimilarityMember
SimilarityResult = MockSimilarityResult

class MockSearchEngine:

    def search(self, query: str, number_of_results=10) -> list[object]:
        result = [mock_speech]
        return result*3 # Return [speech, speech, speech]

    def search_lsa(self, query: str, number_of_results=10) -> list[object]:
        """
        Search using LSA
        :param query: query string
        :param number_of_results: number of results to fetch
        :return: list of
        """
        return self.search("mock")

    def get_available_attributes(self) -> set[str]:
        """
        Get all the attributes the speeches have been grouped by.
        """
        return {"party", "speaker", "speech"}

    def get_attribute_values(self, attribute: str) -> set[str]:
        """
        Get all values for a given attribute
        """
        if attribute == "party":
            return {"nea_dimokratia", "pasok", "oikologoi", "alithino_komma"}
        elif attribute == "speaker" or "member-name":
            return {"samaras", "papandreou", "venizelos", "papoulias", "bakogiannis"}
        else:
            return {"george", "donut", "alpha", "beta", "sigma"}

    def get_keywords(self, attribute: str, attribute_value: str, period_start: date, period_end: date,
                     k=50, custom_stopwords=None) -> list[str]:
        """
        Get the keywords for documents with the given attribute value in the given time period.
        :param k number of keywords to fetch
        :param custom_stopwords set of words that will be ignored in keyword extraction
        :return: ordered list of keywords
        """
        ls = ("this is a mock list of top k keywords foo bar baz spam "*10).split()
        k = len(ls) if len(ls) < k else k
        return ls[:k]

    def predict_party(self, text: str) -> list[str]:
        """
        Try to predict the member of which party said the given text.
        :param text: Text to try to predict
        :return: Which party's member could have said the text.
        """
        predictions = ["george", "donut", "alpha", "beta", "sigma"]
        return predictions

    def get_total_speeches(self) -> int:
        return 100

    def get_most_similar(self, k=50) -> list[tuple[SimilarityMember, SimilarityMember, float]]:
        """
        Get the most similar parliament member pairs.
        :param k: Number of pairs to get
        :return: List with tuples. Each tuple contains: Two SimilarityMember object corresponding to the two members.
                 Their similarity score [0-1].
        """
        return [(mock_similarity_member, mock_similarity_member, 0.56)]*k

    def get_most_similar_to(self, member_name: str, k=10) -> SimilarityResult:
        """
        Returns the k members most similar to the given member.
        :return: SimilarityResult object. See its docs.
        """

        return mock_similarity_result

    def get_similarity_between_members(self, member1_name: str, member2_name: str) -> SimilarityResult:
        """
        Returns the similarity between the given two members.
        :return: SimilarityResult with the given member and one other member.
        """
        m = mock_similarity_result
        m.similar_members = [m.similar_members[0]]
        m.scores = [m.scores[0]]
        return m
