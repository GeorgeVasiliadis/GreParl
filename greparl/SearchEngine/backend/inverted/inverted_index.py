import os
from numpy import sum
from numpy.linalg import norm
import heapq
from math import log, e


class DocEntry:
    """
    An entry in a list in the inverted catalog.
    """

    def __init__(self, document_id, term_frequency):
        self.document_id = document_id
        self.term_frequency = term_frequency

    def get_document_id(self):
        return self.document_id

    def get_term_frequency(self):
        return self.term_frequency


def calculate_tf(word_count):
    return 1 + log(word_count)


def calculate_idf(total_documents, documents_containing_term):
    return log(1 + total_documents / documents_containing_term)


class InvertedIndex:
    def __init__(self, index_file_name="index", replace=False):
        """
        Creates a new empty inverted index, or opens an existing one.
        :param index_file_name: The file name of the new index
        :param replace: Delete the contents of an existing index, if it exists.
        """
        if not os.path.exists("index") or not os.path.isdir("index"):
            os.mkdir("index")
        index_file_name = "index/{}".format(index_file_name)
        # Term offsets are inserted while creating the new index, or when opening an existing index
        self.term_offsets = dict()
        self.lengths = dict()
        # Initialized either in populate_index or in __read_lengths depending on whether the index is new or already
        # exists
        self.total_documents = 0
        if os.path.exists(index_file_name) and not replace:
            # Open existing index
            self.index_contents_file = open(index_file_name, "r", encoding='utf8')
            self.index_catalog_file = open("{}-catalog".format(index_file_name), "r", encoding='utf8')
            self.lengths_file = open("{}-lengths".format(index_file_name), "r", encoding='utf8')
            self.__read_term_offsets()
            self.__read_lengths()
        else:
            # Create a new index
            self.index_contents_file = open(index_file_name, "w+", encoding='utf8')
            self.index_catalog_file = open("{}-catalog".format(index_file_name), "w+", encoding='utf8')
            self.lengths_file = open("{}-lengths".format(index_file_name), "w+", encoding='utf8')

    def populate_index(self, count_matrix, terms) -> None:
        """
        Replace everything in the index using the contents of count_matrix and terms.
        :param count_matrix: An NxM numpy sparse matrix where N is the number of documents and M is the number of
        terms. The element at position i,j contains the number of appearances of term j in document i.
        :param terms: Array with N elements. Element at position j contains the term name for term at column j
        of the count_matrix
        """
        conv_matrix = count_matrix.tocsc()
        total_documents, total_terms = count_matrix.shape
        self.total_documents = total_documents
        for term_index in range(total_terms):
            # Convert column to coo format, so we can quickly iterate over all non-zero elements
            term_column = conv_matrix.getcol(term_index).tocoo()
            term = terms[term_index]
            # Write the offset in the index catalog
            self.index_catalog_file.write(",".join([term, str(self.index_contents_file.tell())]))
            self.index_catalog_file.write("\n")
            # Write the offset in the index dict
            self.term_offsets[term] = self.index_contents_file.tell()
            # Write the contents in the current position in index_contents
            self.index_contents_file.write(self.__create_string_from_term_column(term, term_column))
            self.index_contents_file.write("\n")
        # Store document lengths. This could be done in parallel with the above for loop.
        # Convert to csr for quick row fetching
        conv_matrix = count_matrix.tocsr()
        for document_index in range(total_documents):
            document_row = conv_matrix.getrow(document_index).tocoo()
            document_length = norm(document_row.data)
            self.lengths_file.write(str(document_length))
            self.lengths_file.write("\n")
            self.lengths[document_index] = document_length

    def __create_string_from_term_column(self, term, term_column) -> str:
        """
        Given a term column in COO format, creates a string representation of its contents
        :param term_column: Term column in COO format
        :return: A string corresponding to the index file entry
        """
        # Each line in the index is in the format: term,docid1,count1,docid2,count2,....,docidN,countN
        str_array = [str(term)]
        for document_id, term_frequency in zip(term_column.row, term_column.data):
            str_array.extend([str(document_id), str(term_frequency)])
        return ','.join(str_array)

    def __read_term_offsets(self):
        """
        Reads the term offsets from index_catalog_file into the term_offsets dict.
        """
        self.index_catalog_file.seek(0)
        while line := self.index_catalog_file.readline():
            term, offset = line.removesuffix("\n").split(",")
            self.term_offsets[term] = int(offset)

    def get_term_appearances(self, term: str) -> set[DocEntry]:
        """
        Gets the document and appearance count for each document the term appears in.
        :return: set of DocEntry objects
        """
        if term not in self.term_offsets.keys():
            return set()
        list_contents = set()
        offset = self.term_offsets[term]
        self.index_contents_file.seek(offset)
        line_contents = self.index_contents_file.readline().removesuffix("\n").split(",")
        # The first element of each line is the term. The rest are pairs of doc_id, term_freq
        for i in range(1, len(line_contents), 2):
            document_id = int(line_contents[i])
            term_frequency = int(line_contents[i + 1])
            list_contents.add(DocEntry(document_id, term_frequency))
        return list_contents

    def search(self, query_tokens, number_of_results=10) -> list[int]:
        """
        Searches the catalog for documents matching the query.
        :param query_tokens Query tokenized and processed the same way as the terms in the inverted index.
        :param number_of_results Return the k-top results
        :return List with the document ids of the matching documents best-to-worst.
        """
        document_rankings = {}
        for token in query_tokens:
            document_list = self.get_term_appearances(token)
            idf = calculate_idf(self.total_documents, len(document_list))
            for entry in document_list:
                if entry.get_document_id() not in document_rankings.keys():
                    document_rankings[entry.get_document_id()] = 0
                document_rankings[entry.get_document_id()] += calculate_tf(entry.get_term_frequency())*idf
        for document_id, score in document_rankings.items():
            document_rankings[document_id] = score / self.lengths[document_id]
        return self.__get_best_scores(document_rankings, number_of_results)

    def __get_best_scores(self, scores: dict, number_of_results) -> list[int]:
        score_maxheap = [(score, document_id) for document_id, score in scores.items()]
        heapq.heapify(score_maxheap)
        return [docid for score, docid in heapq.nlargest(number_of_results, score_maxheap)]


    def __read_lengths(self):
        """
        Reads the lengths of each document from the lengths file
        """
        self.lengths = dict()
        self.lengths_file.seek(0)
        document_id = 0
        while line := self.lengths_file.readline():
            length = float(line.removesuffix("\n"))
            self.lengths[document_id] = length
            document_id += 1
        # Store the total document number
        self.total_documents = document_id + 1
