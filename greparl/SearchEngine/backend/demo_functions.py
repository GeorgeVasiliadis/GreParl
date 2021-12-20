from sklearn.feature_extraction.text import CountVectorizer
from ..preprocessing.extract_processed_speeches import extract_processed_speeches
from .inverted.inverted_index import InvertedIndex


def create_inverted_index():
    """
    Create the inverted index from the initial speeches file. Speeches are extracted, tokenized and stemmed before
    being inserted into the index. THe process takes multiple hours.
    """
    extract_processed_speeches("index/speeches.csv", "stemmed-with-stopwords.txt", do_stemming=True,
                               remove_stopwords=False)
    processed_speeches = open("stemmed-with-stopwords.txt", "r", encoding='utf8')
    # Ignore the first line
    processed_speeches.readline()
    lines = processed_speeches.readlines()
    vectorizer = CountVectorizer(lowercase=False)
    count_matrix = vectorizer.fit_transform(lines)
    index = InvertedIndex("index/index")
    index.populate_index(count_matrix, vectorizer.get_feature_names_out())
