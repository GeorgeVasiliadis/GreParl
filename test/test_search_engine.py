import unittest
from datetime import date

from greparl import SearchEngine

class TestSearchEngine(unittest.TestCase):

    def setUp(self):
        self.search_engine = SearchEngine()

    def test_simple_search(self):
        """Search for a very common word that should always return somthing.
        """

        results = self.search_engine.search("ευχαριστώ")
        self.assertTrue(results)

    def test_keywords(self):
        """Make sure that:
        1. at least one attribute is being returned and that
        this attribute contains
        2. at least one value corresponds to that attribute
        3. at  least `k` keywords are being returned
        """

        attributes = self.search_engine.get_available_attributes()
        self.assertTrue(attributes)
        attribute = attributes.pop()

        values = self.search_engine.get_attribute_values(attribute)
        self.assertTrue(values)
        value = values.pop()

        from_date = date(2000, 1, 1)
        to_date = date(2001, 1, 1)

        keywords = self.search_engine.get_keywords(
            attribute,
            value,
            from_date,
            to_date
        )
        self.assertTrue(keywords)

    def test_create_groups(self): ...
