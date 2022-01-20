import pickle
import typing
from dataclasses import dataclass

import numpy as np


@dataclass
class SimilarityMember:
    """
    Represents a member of parliament. Contains their name and a list of the parties they have served with
    """
    name:  str
    parties: list[str]


@dataclass
class SimilarityResult:
    """
    Represent the results of a similarity query. Contains:
    original_member: The member that the similarity query was performed for
    similar_members: List containing the members that are most similar to the original_member. Ordered from highest
                    to lowest similarity.
    scores: Contains the similarity score for each member in similar_members
    """

    original_member: SimilarityMember
    similar_members: list[SimilarityMember]
    scores: list[float]


class SimilarityManager:

    def __init__(self, matrix_file_name="similarity/matrix.pkl", names_file_name="similarity/names.csv"):
        self.similarity_matrix = pickle.load(open(matrix_file_name, "rb"))
        # Dictionary matching the name of every member to their line in the similarity matrix
        self.names_to_rows = {}
        # Dictionary matching the row of every member to their name
        self.rows_to_names = {}
        # Dictionary matching each row of the similarity matrix to the parties of the given member
        self.rows_to_parties = {}
        self._initialize_names_and_parties(open(names_file_name, "r", encoding="utf8"))

    def _initialize_names_and_parties(self, names_file: typing.IO) -> None:
        """
        Reads the names and parties from the given names_file. Populates the names and parties dicts
        :param names_file: file
        """
        row = 0
        while line := names_file.readline():
            split = line.split(",")
            self.rows_to_names[row] = split[0]
            self.names_to_rows[split[0]] = row
            self.rows_to_parties[row] = [party_name.removesuffix("\n") for party_name in split[1:]]
            row += 1

    def get_similarity_between_members(self, member_name1: str, member_name2: str):
        self._verify_member_exists(member_name1)
        self._verify_member_exists(member_name2)
        member_row1 = self.names_to_rows[member_name1]
        member_row2 = self.names_to_rows[member_name2]
        member1 = SimilarityMember(member_name1, self.rows_to_parties[member_row1])
        member2 = SimilarityMember(member_name2, self.rows_to_parties[member_row2])
        similarity_score = self.similarity_matrix[member_row1][member_row2]
        match = SimilarityResult(original_member=member1, similar_members=[member2], scores=[float(similarity_score)])
        return match

    def _verify_member_exists(self, member_name):
        """
        Checks if the given member exists. If not throws RuntimeError
        """
        if member_name not in self.names_to_rows.keys():
            raise RuntimeError("Member {} does not exist".format(member_name))

    def get_most_similar_to(self, member_name: str, k=10) -> SimilarityResult:
        """
        Get the k most similar members to the given member.
        :param member_name: search for members similar to this member
        :param k: get the k most similar members
        :return: the results of the search
        """
        self._verify_member_exists(member_name)
        member_row = self.names_to_rows[member_name]
        member_similarities = self.similarity_matrix[member_row]
        # The document with itself has similarity 1, the maximum. So, we need to get the top k+1 similarities and
        # then ignore the first.
        top_similarities_indexes = np.argpartition(member_similarities, -k - 1)[(-k - 1):]
        # https://stackoverflow.com/questions/6910641/how-do-i-get-indices-of-n-maximum-values-in-a-numpy-array
        # Sort the indexes according to the scores
        top_similarities_indexes = top_similarities_indexes[np.argsort(member_similarities[top_similarities_indexes])]
        original_member = SimilarityMember(member_name, self.rows_to_parties[member_row])
        similar_members = []
        scores = []
        # Ignore the most similar document
        top_similarities_indexes = top_similarities_indexes[:-1]
        for other_member_row in top_similarities_indexes[::-1]:
            score = float(member_similarities[other_member_row])
            other_member = self._get_member_from_row(other_member_row)
            similar_members.append(other_member)
            scores.append(score)
        return SimilarityResult(original_member, similar_members, scores)

    def _get_member_from_row(self, row: int) -> SimilarityMember:
        """
        Get a SimilarityMember object from a row number
        """
        member_name = self.rows_to_names[row]
        parties = self.rows_to_parties[row]
        return SimilarityMember(member_name, parties)

    def get_most_similar(self, k=50) -> list[tuple[SimilarityMember, SimilarityMember, float]]:
        """
        Get the k most similar member pairs.
        :return list with k elements from most to least similar
        """
        # The similarity matrix is symmetric, so we can search through the upper triangular matrix to find the pairs.
        upper_triangular = self.similarity_matrix
        for i in range(0, upper_triangular.shape[1]):
            for j in range(0, i+1):
                upper_triangular[i][j] = 0
        # Get the k largest elements.
        indexes = np.argpartition(-upper_triangular.ravel(), k)[:k]
        indexes = np.column_stack(np.unravel_index(indexes, upper_triangular.shape))
        # Create a list containing the similarity score of each pair and the indexes of the pairs.
        scores_with_indexes = []
        for index in indexes:
            scores_with_indexes.append([upper_triangular[index[0], index[1]], *index])
        # Sort the list according to the scores
        scores_with_indexes = np.array(scores_with_indexes)
        scores_with_indexes = scores_with_indexes[scores_with_indexes[:, 0].argsort()]
        # Assemble the results. Scores with indexes is sorted ascending.
        results = []
        for score, member_row1, member_row2 in scores_with_indexes[::-1]:
            member1 = self._get_member_from_row(member_row1)
            member2 = self._get_member_from_row(member_row2)
            results.append((member1, member2, score))
        return results
