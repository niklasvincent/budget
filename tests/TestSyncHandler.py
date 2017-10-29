import json
import os
import sys
import unittest

import oauth2

from collections import defaultdict
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

    @classmethod
    def _load_json(self, filename):
        absolute_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
        with open(absolute_filename, 'r') as f:
            data = json.load(f)
        return data

    def _splitwise_with_mocked_expenses(self, filename):
        expenses = self._load_json(filename)
        categories = self._load_json("data/categories.json")
        m = Mock()

        self.requested_urls = []

        def mock_request(url):
            self.requested_urls.append(url)
            if "get_expenses" in url:
                return expenses
            if "get_categories" in url:
                return categories

        m.side_effect = mock_request
        self.splitwise.request = m

    def _fixer_with_mocked_conversion_rate(self):
        m = Mock()

        def mock_currency_conversion(for_date, from_currency, to_currency):
            return 0.09

        m.side_effect = mock_currency_conversion
        self.fixer.get_conversion_rate = m

    def setUp(self):
        self.person = Person("Test User", 1234, "test@example.com", defaultdict(lambda: "Expense"), "GBP", "abc", "xyz", [])
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

        # Mock external services
        self._splitwise_with_mocked_expenses("data/expenses/mixed-expenses-sync.json")
        self._fixer_with_mocked_conversion_rate()

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

            # Mock external service again to cause deletion of expense
            self._splitwise_with_mocked_expenses("data/expenses/mixed-expenses-sync-deletion.json")

            self.sync_handler.execute()

            self.assertEquals(
                self.sync_handler.nbr_of_deletes,
                1
            )
            expenses = self.db.get_expenses(user_id=1234)
            self.assertEquals(
                len(expenses),
                3,
                "Wrong number of expenses in database after deleting one"
            )

            expected_after_deletion = [
                ("Sushi", 4.33, "SEK", date(2016, 5, 8)),
                ("Licquorice", 3.33, "DKK", date(2016, 5, 8)),
                ("Groceries", 4.3, "GBP", date(2016, 5, 2))
            ]
            for index, expense in enumerate(expenses):
                self.assertEquals(
                    expense.description,
                    expected_after_deletion[index][0],
                )
                self.assertEquals(
                    expense.cost,
                    expected_after_deletion[index][1],
                )
                self.assertEquals(
                    expense.original_currency,
                    expected_after_deletion[index][2],
                )
                self.assertEquals(
                    expense.created_at.date(),
                    expected_after_deletion[index][3],
                )


def main():
    unittest.main()

if __name__ == '__main__':
    main()