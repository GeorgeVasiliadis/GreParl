import os
import pickle
from typing import Dict

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import linear_kernel

from .extract_processed_speeches import extract_processed_speeches
from .funcs import remove_accents
from .stopwords import STOPWORDS
from ..backend.inverted.inverted_index import InvertedIndex
from ..backend.top.suggested_stopwords import suggested_stopwords
from .create_group import *
from .create_lsa import *
from .create_ai import create_sampled_model


def create_inverted_index(processed_speeches_file_name,
                          index_file_name="index", speeches_file="speeches.csv",speech_number=-1):
    """
    Create the inverted index from the initial speeches file. Speeches are extracted, tokenized and stemmed before
    being inserted into the index. The process takes multiple hours for all speeches.
    :param processed_speeches_file_name File containing the speeches' contents with any preprocessing applied

    :param speech_number number of speeches to include in the index, if -1 include all speeches
    """
    processed_speeches = open(processed_speeches_file_name, "r", encoding='utf8')
    # Ignore the first line
    processed_speeches.readline()
    lines = processed_speeches.readlines()
    vectorizer = CountVectorizer(lowercase=False)
    count_matrix = vectorizer.fit_transform(lines)
    index = InvertedIndex(index_file_name)
    index.populate_index(count_matrix, vectorizer.get_feature_names_out())


def create_transformer_vectorizer(speech_file: SpeechFile) -> None:
    """
    Creates a CountVectorizer and TfIdf transformer trained on all speeches of the given speech file. Stores them
    in the folder tfidf
    :param speech_file: File containing all the speeches
    """
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


def create_similarity_matrix(grouped_speeches: Dict[str, list[Speech]], vectorizer: CountVectorizer,
                             transformer: TfidfTransformer) -> None:
    """
    Create the similarity matrix for the given speeches. The speeches for each group are first concatenated into one
    speech. Then, the TF-IDF score is calculated by treating each group as a document. Then the cosine similarity for
    all pairs is calculated and stored on disk.
    :param grouped_speeches: Dictionary matching each group to a list of Speech objects
    :param vectorizer: A CountVectorizer trained on all speeches.
    :param transformer: A TfidfTransformer trained on all speeches.
    """
    # Create a document for each group, containing all the speeches for the group concatenated into one string.
    # Store the group names in an array, and the documents in a parallel array. For each group create a list
    # with the political parties it has represented.
    group_names = []
    group_documents = []
    group_parties = defaultdict(set)
    for group_name, speeches in grouped_speeches.items():
        # Ignore group with empty name (speeches have no value for the group)
        if group_name == "":
            continue
        group_names.append(group_name)
        group_speech_contents = []
        for speech in speeches:
            group_speech_contents.append(speech.contents)
            group_parties[group_name].add(speech.political_party)
        group_documents.append(".".join(group_speech_contents))
    del group_speech_contents
    del grouped_speeches
    # Create the TF-IDF matrix
    counts = vectorizer.transform(group_documents)
    tfidf_matrix = transformer.transform(counts)
    # We don't need the count matrix anymore, or the speeches
    del counts
    # List containing an array for each document
    document_similarities = []
    # Code based on this: https://stackoverflow.com/questions/12118720/python-tf-idf-cosine-to-find-document-similarity
    # For all documents, calculate their similarity with all other documents.
    for i in range(tfidf_matrix.shape[0]):
        cosine_similarity = linear_kernel(tfidf_matrix[i:i+1], tfidf_matrix).flatten()
        document_similarities.append(cosine_similarity)
    document_similarities = np.array(document_similarities)
    # Write the similarity matrix into a file
    pickle.dump(document_similarities, open("similarity/matrix.pkl", "wb"))
    # Write the group names and parties into a file
    with open("similarity/names.csv", "w", encoding="utf8") as file:
        for name in group_names:
            group_string = "{},".format(name) + ",".join(group_parties[name])
            file.write(group_string)
            file.write("\n")
        # Delete last newline
        file.seek(0, os.SEEK_END)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.truncate()


def create_folder_if_not_exists(folder_name: str):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


def create_all(speeches_to_include_in_index=-1, lsa_speeches=100000):
    """
    Creates all the necessary files necessary for the program to function. Creating everything from scratch should
    take about 1.5-2 hours for all speeches. The majority of time is spent creating the inverted index.
    :param speeches_to_include_in_index If -1 include all speeches, else include only the first n speeches in the
                                        inverted index.
    :param lsa_speeches Speeches to use in LSA
    """
    speeches_file_name = "speeches.csv"
    speeches_file = SpeechFile("speeches.csv")
    processed_speeches_file_name = "processed/stemmed-with-stopwords.txt"
    # Create the processed speeches file, necessary for the inverted index
    create_folder_if_not_exists("processed")
    extract_processed_speeches(speeches_file_name, processed_speeches_file_name, limit=speeches_to_include_in_index)
    # Create the inverted index using the previously generated speeches file
    create_folder_if_not_exists("index")
    create_inverted_index(processed_speeches_file_name, speeches_file=speeches_file_name,
                          speech_number=speeches_to_include_in_index)
    # Create the CountVectorizer and TfidfTransformer trained on all speeches, and used for keyword extraction
    # and similarity.
    create_folder_if_not_exists("tfidf")
    create_transformer_vectorizer(speeches_file)
    # Create the group files, used for grouping speeches by attribute. Group by party and member_name.
    create_folder_if_not_exists("group")
    create_groups(speeches_file, [party, speaker_name], replace=True)
    # Create the similarity matrix
    # First group all speeches by member name for similarity matching
    member_name_grouped_speeches = defaultdict(list)
    # Group speeches by year for LSA
    date_grouped_speeches = defaultdict(list)
    # Group speeches by party for model training
    party_grouped_speeches = defaultdict(list)
    for speech in speeches_file.speeches():
        member_name_grouped_speeches[speech.member_name].append(speech)
        date_grouped_speeches[speech.sitting_date.year].append(speech)
        party_grouped_speeches[speech.political_party].append(speech)
    # Use the previously generated vectorizer and transformer
    vectorizer = pickle.load(open("tfidf/vectorizer.pkl", "rb"))
    transformer = pickle.load(open("tfidf/transformer.pkl", "rb"))
    # Create the similarity matrix
    create_folder_if_not_exists("similarity")
    create_similarity_matrix(member_name_grouped_speeches, vectorizer, transformer)
    del member_name_grouped_speeches
    processed_speeches_file = open(processed_speeches_file_name, "r", encoding="utf8")
    create_folder_if_not_exists("lsa")
    create_sampled_lsa(date_grouped_speeches, processed_speeches_file, speeches_in_lsa=lsa_speeches)
    del date_grouped_speeches
    # We can use the vectorizer created from lsa, that has been trained on the processed speeches
    processed_speeches_vectorizer = pickle.load(open("lsa/vectorizer.pkl", "rb"))
    create_sampled_model(party_grouped_speeches, processed_speeches_file, processed_speeches_vectorizer,
                         sample_size=100000)
