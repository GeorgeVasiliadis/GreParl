from datetime import date

from .MockSpeech import mock_speech

class MockSearchEngine:

    def search(self, query: str, number_of_results=10) -> list[object]:
        result = [mock_speech]
        return result*3 # Return [speech, speech, speech]

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
        elif attribute == "speaker":
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
