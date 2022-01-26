from dataclasses import dataclass

@dataclass
class MockSimilarityMember:
    """
    Represents a member of parliament. Contains their name and a list of the parties they have served with
    """
    name:  str
    parties: list[str]

mock_similarity_member = MockSimilarityMember(
    "Real Name",
    "Party1 Party2 Party3 Party4".split()
)

@dataclass
class MockSimilarityResult:
    """
    Represent the results of a similarity query. Contains:
    original_member: The member that the similarity query was performed for
    similar_members: List containing the members that are most similar to the original_member. Ordered from highest
                    to lowest similarity.
    scores: Contains the similarity score for each member in similar_members
    """

    original_member: MockSimilarityMember
    similar_members: list[MockSimilarityMember]
    scores: list[float]

mock_similarity_result = MockSimilarityResult(
    mock_similarity_member,
    [mock_similarity_member]*4,
    [0.5, 0.35, 0.62, 3]
)
