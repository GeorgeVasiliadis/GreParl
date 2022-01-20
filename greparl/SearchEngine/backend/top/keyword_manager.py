import copy
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer


def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    """get the feature names and tf-idf score of top n items"""

    # use only topn items from vector
    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []

    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        # keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    # create a tuples of feature,score
    # results = zip(feature_vals,score_vals)
    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]

    return results


class KeywordManager:
    """
    Class used for keyword extraction from documents.
    """
    def __init__(self, vectorizer: CountVectorizer, transformer: TfidfTransformer):
        self.vectorizer = vectorizer
        self.transformer = transformer

    def get_keywords(self, document: str, k: int = 10, custom_stopwords: set = None):
        """
        Get the top-k keywords from the given document.
        :param document: Text to find keywords for
        :param k: Number of keywords to return
        :param custom_stopwords: Set containing additional stopwords that will be ignored during keyword extraction
        :return: Ordered list with the top-k keywords, from most to least representative.
        """
        if custom_stopwords is None:
            custom_stopwords = set()
        # Copy the vectorizer and add some stopwords
        vectorizer = self.vectorizer
        # Create a copy of the original vectorizer and add the custom stopwords
        if custom_stopwords is not None:
            vectorizer = copy.deepcopy(self.vectorizer)
        vectorizer.stop_words.extend(custom_stopwords)
        # Get term counts for the document
        document_row = vectorizer.transform([document])
        # Transform the counts into tf-idf values
        tfidf_row = self.transformer.transform(document_row).tocoo()
        # Get the top keywords
        keywords_with_scores = extract_topn_from_vector(vectorizer.get_feature_names_out(), sort_coo(tfidf_row),
                                                        topn=k)
        return list(keywords_with_scores.keys())


