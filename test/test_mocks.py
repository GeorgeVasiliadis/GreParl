import unittest

from mock.MockSearchEngine import MockSearchEngine as MSE

class TestMockSearchEngine(unittest.TestCase):

    def test_search(self):
        results = MSE().search("mock")
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
        keywords = MSE().get_keywords("mock", "mock", "mock", "mock")
        self.assertIs(type(keywords), list)
        self.assertTrue(keywords)
