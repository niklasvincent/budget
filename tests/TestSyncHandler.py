import json
import os
import sys
import unittest

import oauth2

from datetime import date, datetime

from mock import Mock, MagicMock

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../budget'))
sys.path.insert(1, path)

from config import Person
from database import *
from fixer import Fixer
from splitwise import Splitwise
from sync_handler import SyncHandler


class TestSyncHandler(unittest.TestCase):

    def _load_json(self, filename):
        absolute_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
        with open(absolute_filename, 'r') as f:
            data = json.load(f)
        return data

    def setUp(self):
        self.person = Person("Test User", 1234, "GBP", "abc", "xyz")
        self.consumer = oauth2.Consumer("def", "jkl")
        self.splitwise = Splitwise(self.consumer, self.person)
        self.db = Database("sqlite:///:memory:")
        self.db.create_tables()
        self.fixer = Fixer()

        self.sync_handler = SyncHandler(
            db=self.db,
            person=self.person,
            splitwise=self.splitwise,
            fixer=self.fixer
        )

    def testSyncFromScratch(self):
        self.db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 5, 0),
            user_id=self.person.user_id,
            success=True,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        self.db.add_currency_conversion(
            for_date=date(2016, 5, 8),
            from_currency="SEK",
            to_currency="GBP",
            rate=0.08
        )
        m = Mock()

        def mock_currency_conversion(for_date, from_currency, to_currency):
            return 0.09

        m.side_effect = mock_currency_conversion
        self.fixer.get_conversion_rate = m

        expenses = self._load_json("data/expenses/mixed-expenses-sync.json")
        categories = self._load_json("data/categories.json")
        m = Mock()

        requested_urls = []

        def mock_request(url):
            requested_urls.append(url)
            if "get_expenses" in url:
                return expenses
            if "get_categories" in url:
                return categories

        m.side_effect = mock_request
        self.splitwise.request = m

        self.sync_handler.execute()

        marker = self.db.get_last_successful_marker(user_id=1234)
        self.assertNotEquals(
            marker.created_at,
            datetime(2016, 10, 22, 12, 5, 0)
        )

        expected = [
            ("Sushi", 4.33, "SEK", date(2016, 5, 8)),
            ("Shoes", 5.79, "SEK", date(2016, 5, 8)),
            ("Licquorice", 3.33, "DKK", date(2016, 5, 8)),
            ("Groceries", 4.3, "GBP", date(2016, 5, 2))
        ]

        expenses = self.db.get_expenses(user_id=1234)
        self.assertEquals(
            len(expenses),
            4,
            "Wrong number of expenses in database"
        )
        for index, expense in enumerate(expenses):
            self.assertEquals(
                expense.description,
                expected[index][0],
            )
            self.assertEquals(
                expense.cost,
                expected[index][1],
            )
            self.assertEquals(
                expense.original_currency,
                expected[index][2],
            )
            self.assertEquals(
                expense.created_at.date(),
                expected[index][3],
            )


def main():
    unittest.main()

if __name__ == '__main__':
    main()