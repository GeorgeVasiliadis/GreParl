import unittest

from mock.MockSearchEngine import MockSearchEngine as MSE

class TestMockSearchEngine(unittest.TestCase):

    def test_search(self):
        results = MSE().search("mock")
        self.assertIs(type(results), list)
        self.assertTrue(results)

    def test_search_lsa(self):
        results = MSE().search_lsa("mock")
        self.assertIs(type(results), list)
        self.assertTrue(results)

    def test_get_available_attributes(self):
        attributes = MSE().get_available_attributes()
        self.assertIs(type(attributes), set)
        self.assertTrue(attributes)

    def test_get_attribute_values(self):
        values = MSE().get_attribute_values("mock")
        self.assertIs(type(values), set)
        self.assertTrue(values)

    def test_get_keywords(self):
        # Simple case
        keywords = MSE().get_keywords("mock", "mock", "mock", "mock")
        self.assertIs(type(keywords), list)
        self.assertTrue(keywords)

        # Request more than available
        keywords = MSE().get_keywords("mock", "mock", "mock", "mock", k=10000)
        self.assertIs(type(keywords), list)
        self.assertTrue(keywords)

        # Request less than available
        k=3
        keywords = MSE().get_keywords("mock", "mock", "mock", "mock", k=k)
        self.assertIs(type(keywords), list)
        self.assertTrue(keywords)
        self.assertEqual(len(keywords), k)


    def test_get_most_similar(self):
        results = MSE().get_most_similar(10)
        self.assertTrue(results)
        self.assertEqual(len(results), 10)

    def test_get_most_similar_to(self):
        result = MSE().get_most_similar_to("Bobos", 10)
        self.assertTrue(result)


    def test_get_similarity_between_members(self):
        results = MSE().get_similarity_between_members("Bobos", "Robos")
        self.assertTrue(results)
