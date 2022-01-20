import pickle
import typing
from sklearn.metrics.pairwise import cosine_similarity


class LSAManager:
    """
    Manages searches using LSA. Intended to be used only as a demo. Since LSA matrices are large, this class does
    not keep them in memory, instead loading the matrices for each query executed.
    """

    def _load_translations(self, translation_file: typing.IO):
        self.row_to_speech_id = dict()
        translation_file.seek(0)
        while line := translation_file.readline():
            if line != "":
                line, speech_id = line.removesuffix("\n").split(",")
                self.row_to_speech_id[int(line)] = int(speech_id)

    def __init__(self, matrix_file="lsa/matrix.pkl", svd_file="lsa/svd.pkl", translation_file="lsa/translation",
                 vectorizer_file="lsa/vectorizer.pkl"):
        self.vectorizer = pickle.load(open(vectorizer_file, "rb"))
        self._load_translations(open(translation_file, "r", encoding="utf8"))
        self.matrix_file = open(matrix_file, "rb")
        self.svd_file = open(svd_file, "rb")

    def search(self, query_tokens: list[str], k=50) -> list[int]:
        """
        Search for the top-k documents using the LSA.
        :param query_tokens: the tokens of the query. must be stemmed and processed if the LSA matrices were
        :param k fetch the top-k most relative documents
        :return: list with the speech ids of most to least relevant speeches
        """
        # Seek to the start of the files
        self.svd_file.seek(0)
        self.matrix_file.seek(0)
        # Load the TruncatedSVD and the document-to-topic matrix
        svd = pickle.load(self.svd_file)
        document_matrix = pickle.load(self.matrix_file)
        # First we need to calculate the TF-IDF values of the query
        query_vector = self.vectorizer.transform([" ".join(query_tokens)])
        # Then perform dimensionality reduction
        query_vector = svd.transform(query_vector)
        # We need to calculate the cosine similarity of the query vector with all other documents
        similarities = cosine_similarity(query_vector, document_matrix).flatten()
        similar_docs_rows = similarities.argsort()[:-k-1:-1]
        # Translate the row ids to speech ids
        speech_ids = [self.row_to_speech_id[row_id] for row_id in similar_docs_rows.tolist()]
        return speech_ids
