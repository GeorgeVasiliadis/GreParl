import os
import pickle

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from .extract_processed_speeches import extract_processed_speeches
from .funcs import remove_punctuation, remove_accents
from .stopwords import STOPWORDS
from ..backend.inverted.inverted_index import InvertedIndex
from ..backend.speech_file import SpeechFile
from ..backend.top.suggested_stopwords import suggested_stopwords


def create_inverted_index(index_file_name="index", speeches_file="speeches.csv", speech_number=100):
    """
    Create the inverted index from the initial speeches file. Speeches are extracted, tokenized and stemmed before
    being inserted into the index. THe process takes multiple hours.
    :param speech_number number of speeches to include in the index
    """
    if not os.path.exists("processed"):
        os.mkdir("processed")
    extract_processed_speeches(speeches_file, "processed/stemmed-with-stopwords.txt", do_stemming=True,
                               remove_stopwords=False, limit=speech_number)
    processed_speeches = open("processed/stemmed-with-stopwords.txt", "r", encoding='utf8')
    # Ignore the first line
    processed_speeches.readline()
    lines = processed_speeches.readlines()
    vectorizer = CountVectorizer(lowercase=False)
    count_matrix = vectorizer.fit_transform(lines)
    index = InvertedIndex(index_file_name)
    index.populate_index(count_matrix, vectorizer.get_feature_names_out())


def create_keyword_transformer_vectorizer(speech_file: SpeechFile):
    speeches = [s.contents for s in speech_file.speeches()]
    # Remove accents from stopwords
    normalized_stopwords = STOPWORDS
    STOPWORDS.extend(suggested_stopwords)
    normalized_stopwords = remove_accents(list(normalized_stopwords))
    # Create a count vectorizer and get the count matrix for all speeches
    vectorizer = CountVectorizer(strip_accents='unicode', stop_words=normalized_stopwords)
    count_matrix = vectorizer.fit_transform(speeches)
    # Create a transformer and calculate the IDF values for the whole corpus
    transformer = TfidfTransformer()
    transformer.fit(count_matrix)
    # Save to file
    pickle.dump(vectorizer, open("tfidf/vectorizer.pkl", "wb"))
    pickle.dump(transformer, open("tfidf/transformer.pkl", "wb"))
