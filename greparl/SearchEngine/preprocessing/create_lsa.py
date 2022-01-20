import io
import os
import pickle
import random
import typing
from collections import Counter
from typing import Dict, Any

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from .. import Speech

__all__ = [
    'create_sampled_lsa'
]


def sample_speeches(grouped_speeches: Dict[Any, list[Any]], sample_size) -> list[Speech]:
    """
    Samples speeches from each group in group speeches, so that the distribution remains the same.

    For example, if there are 100 total speeches in grouped speeches and 50 belong to a specific group, that group
    makes up 50% of the total speeches. If the sample size is 50, then 25 of the speeches in the sample will come
    from that group.
    :param grouped_speeches: Speeches grouped by an arbitrary attribute
    :param sample_size: Number of speeches to be included in the sample
    :return: list of the sampled speeches
    """
    # Calculate the total speeches, in all groups
    total_speeches = sum([len(s) for s in grouped_speeches.values()])
    if sample_size > total_speeches:
        raise RuntimeError("Sample size cannot be larger than the total number of speeches.")
    # Create a list with all the groups that we can pick and the weight of each group
    population = []
    weights = []
    for group_name, group_speeches in grouped_speeches.items():
        group_weight = len(group_speeches)/total_speeches
        weights.append(group_weight)
        population.append(group_name)
    # Pick sample_size items from all possible groups, according to the calculated distribution.
    samples = random.choices(population, weights, k=sample_size)
    # Calculate how many elements we need from each group
    grouped_samples = Counter(samples)
    # Retrieve the speeches from each group
    sampled_speeches = []
    for group_name, speeches_count in grouped_samples.items():
        # Get speeches_count speeches from the group with group_name
        sampled_speeches.extend(random.sample(grouped_speeches[group_name], speeches_count))
    return sampled_speeches


def get_lines_from_file(file: typing.IO, lines: list[int]) -> list[str]:
    """
    Get the given lines from the given file. Lines are 0 indexed. Line numbers are sorted and returned in that order.
    If lines is already sorted, then the lines will be in the same order.
    :param file: file to get the lines from
    :param lines: list with line numbers
    :return: list with the lines as strings and with newlines removed
    """
    file.seek(0)
    lines.sort()
    current_line = 0
    line_contents = []
    while (len(lines) > 0) and (line := file.readline()):
        if lines[0] == current_line:
            line_contents.append(line.removesuffix("\n"))
            lines.pop(0)
        current_line += 1
    return line_contents


def get_processed_speeches(processed_speeches_file: typing.IO, speeches: list[Speech]) -> list[tuple[Speech, str]]:
    """
    Given a list of speeches and the processed speeches file, returns pairs of Speech and the processed speech.
    :param processed_speeches_file: File containing the processed speeches, with 1-1 correspondence to the original
                                    speeches csv.
    :param speeches: List of speeches to be fetched
    :return: list with tuples of (Speech, processed speech text)
    """

    # Sort the speeches in ascending order
    speeches.sort(key=lambda speech: speech.id)
    # The processed speeches are in the same order as in the speeches list, since the speeches are sorted by
    # id and increasing ids correspond to increasing line numbers
    # Speech with ID 0 is in line 1, ID 1 in line 2, etc. because the first line is not a speech.
    processed_speeches = get_lines_from_file(processed_speeches_file, [(speech.id + 1) for speech in speeches])
    return list(zip(speeches, processed_speeches))


def create_sampled_lsa(grouped_speeches: Dict[Any, list[Speech]], processed_speeches_file: typing.IO,
                       speeches_in_lsa=100000) -> None:
    """
    Create the necessary files for LSA. LSA requires lots of RAM for all speeches, so we sample some of each group, in
    the grouped_speeches dict. The speeches are sampled according to the
    :param grouped_speeches: All speeches of the file split into groups.
    :param processed_speeches_file: File containing the processed speeches, with 1-1 correspondence to the original
                                    speeches csv.
    :param speeches_in_lsa: How many speeches to include in the generated LSA files.
    """
    # Sample speeches according to the given grouping
    sampled_speeches = sample_speeches(grouped_speeches, speeches_in_lsa)
    del grouped_speeches
    sampled_speeches = get_processed_speeches(processed_speeches_file, sampled_speeches)
    # First, we need to create a translation table between the line numbers in the matrix and the speech IDs.
    translation_table = dict([(matrix_row, speech_with_processed[0].id) for matrix_row, speech_with_processed in
                              enumerate(sampled_speeches)])
    # Write the translation table to disk.
    with open("lsa/translation", "w", encoding="utf8") as translation_file:
        translation_file.writelines([(",".join([str(row), str(sid)])) + "\n" for row, sid in translation_table.items()])
        # Remove last newline
        translation_file.seek(0, os.SEEK_END)
        translation_file.seek(translation_file.tell() - 1, os.SEEK_SET)
        translation_file.truncate()
    del translation_table
    # Tuned according to this
    # https://scikit-learn.org/stable/modules/decomposition.html#truncated-singular-value-decomposition-and-latent-semantic-analysis
    vectorizer = TfidfVectorizer(lowercase=False, sublinear_tf=True, use_idf=True)
    # Create the TF-IDF table for the processed speeches
    X = vectorizer.fit_transform([processed for _, processed in sampled_speeches])
    del sampled_speeches
    # Use 300 "topics" on SVD
    svd = TruncatedSVD(n_components=300)
    # X_new is speeches_in_lsa x 300
    X_new = svd.fit_transform(X)
    del X
    # Save the X_new matrix and the svd object that will be helpful in future transformations
    pickle.dump(svd, open("lsa/svd.pkl", "wb"))
    pickle.dump(X_new, open("lsa/matrix.pkl", "wb"))
    pickle.dump(vectorizer, open("lsa/vectorizer.pkl", "wb"))
