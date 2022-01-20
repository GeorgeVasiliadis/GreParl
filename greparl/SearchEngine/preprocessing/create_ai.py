import gzip
import pickle
from typing import Callable, IO, Dict, Any

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

from ..backend.speech_file import Speech, SpeechFile
from .create_lsa import sample_speeches, get_processed_speeches


def _combine_speeches_with_processed(speech_file: SpeechFile, processed_speeches_file: IO) \
        -> tuple[list[Speech], list[str]]:
    """
    Create pairs of Speech objects with their corresponding processed contents.
    :param speech_file: File containing the original speeches
    :param processed_speeches_file: File containing the processed speeches, with 1-1 correspondence to the original
                                    speeches csv.
    :return: Two lists. The first contains the original speeches, the second list contains the corresponding processed
            speeches.
    """
    original_speeches = [s for s in speech_file.speeches()]
    processed_speeches = [line.removesuffix("\n") for line in processed_speeches_file.readlines()]
    # The first line of the processed file is empty
    processed_speeches.pop(0)
    return original_speeches, processed_speeches


def create_model(speeches_with_processed: list[tuple[Speech, str]], vectorizer: TfidfVectorizer,
                 attribute: Callable[[Speech], str] = lambda speech: speech.political_party,
                 attribute_name: str = 'party'):
    """
    :param speeches_with_processed list of tuples containing a speech and its corresponding processed speech text
    :param vectorizer TfidfVectorizer trained on the processed documents.
    :param attribute Callable mapping each Speech object to a string. Is used to extract the property that will be
                     predicted by the model. By default, is set to return the political_party of the speech.
    :param attribute_name Name of the attribute, used when saving the model.
    """
    original_speeches, processed_speeches = zip(*speeches_with_processed)
    # Use the vectorizer to create the TF-IDF matrix.
    tf_matrix = vectorizer.transform(processed_speeches)
    del processed_speeches
    # Create the labels
    labels = [attribute(speech) for speech in original_speeches]
    del original_speeches
    data_train, data_test, labels_train, labels_test = train_test_split(tf_matrix, labels)
    clf = RandomForestClassifier(n_jobs=2)
    clf.fit(data_train, labels_train)
    labels_predicted = clf.predict(data_test)
    print(classification_report(labels_test, labels_predicted))
    print("The accuracy score is {:.2%}".format(accuracy_score(labels_test, labels_predicted)))
    pickle.dump(clf, gzip.open("models/{}".format(attribute_name), "wb"))


def create_sampled_model(grouped_speeches: Dict[Any, list[Speech]], processed_speeches_file: IO,
                         vectorizer: TfidfVectorizer, sample_size=100000):
    """
    Create sampling from the given speeches.
    :param grouped_speeches: Speeches grouped according to an attribute
    :param processed_speeches_file: File containing the processed speeches, with 1-1 correspondence to the original
                                    speeches csv.
    :param vectorizer TfidfVectorizer trained on the processed documents.
    :param sample_size: Number of speeches to include in sample
    """
    samples = sample_speeches(grouped_speeches, sample_size)
    samples = get_processed_speeches(processed_speeches_file, samples)
    create_model(samples, vectorizer)
