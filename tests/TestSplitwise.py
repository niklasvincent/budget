import json
import os
import sys
import unittest

import oauth2

from datetime import datetime

from mock import Mock, MagicMock

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../budget'))
sys.path.insert(1, path)

from config import Person
from splitwise import *


class TestSplitwise(unittest.TestCase):

    def _load_json(self, filename):
        absolute_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
        with open(absolute_filename, 'r') as f:
            data = json.load(f)
        return data

    def setUp(self):
        self.person = Person("Test User", 1234, "GBP", "abc", "xyz")
        self.consumer = oauth2.Consumer("def", "jkl")

    def testBuildUrl(self):
        splitwise = Splitwise(self.consumer, self.person)
        url = splitwise._build_url("get_expenses", {"limit": "0"})
        self.assertEquals(
            url,
            "https://secure.splitwise.com/api/v3.0/get_expenses?limit=0",
            "URL does not match"
        )

    def testParseDateWithoutTimeZone(self):
        splitwise = Splitwise(self.consumer, self.person)
        unaware = datetime(2015, 4, 18, 15, 30, 35)
        parsed = splitwise._parse_date("2015-04-18T15:30:35Z")
        self.assertEqual(
            parsed,
            unaware,
            "Datetime is not time zone unaware or not parsed correctly"
        )

    def testGetUserShareNonZero(self):
        splitwise = Splitwise(self.consumer, self.person)
        expenses = self._load_json("data/expenses/non-zero-sum-expense.json")
        cost = splitwise._get_user_share(expenses.get("expenses")[0])
        self.assertEquals(
            cost,
            5.71,
            "Cost did not match: %f" % cost
        )
        self.assertIsInstance(splitwise._get_user_share(expenses.get("expenses")[0]), float, "Not a float")

    def testGetUserShareZero(self):
        splitwise = Splitwise(self.consumer, self.person)
        expenses = self._load_json("data/expenses/zero-sum-expense.json")
        cost = splitwise._get_user_share(expenses.get("expenses")[0])
        self.assertEquals(
            cost,
            0.0,
            "Cost did not match: %f" % cost
        )
        self.assertIsInstance(splitwise._get_user_share(expenses.get("expenses")[0]), float, "Not a float")

    def testNonZeroSumExpenseIsIncluded(self):
        splitwise = Splitwise(self.consumer, self.person)
        expenses = self._load_json("data/expenses/non-zero-sum-expense.json")
        self.assertTrue(
            splitwise._is_applicable_expense(expenses.get("expenses")[0]),
            "Expense should be applicable"
        )

    def testZeroSumExpenseIsExcluded(self):
        splitwise = Splitwise(self.consumer, self.person)
        expenses = self._load_json("data/expenses/zero-sum-expense.json")
        self.assertFalse(
            splitwise._is_applicable_expense(expenses.get("expenses")[0]),
            "Expense should be non-applicable"
        )

    def testGetExpenses(self):
        splitwise = Splitwise(self.consumer, self.person)
        expenses = self._load_json("data/expenses/mixed-expenses.json")
        categories = self._load_json("data/categories.json")
        m = Mock()
        m.side_effect = [categories, expenses]
        splitwise.request = m
        expenses = splitwise.get_expenses()
        self.assertEquals(
            len(expenses),
            8,
            "Wrong number of expenses"
        )


def main():
    unittest.main()

if __name__ == '__main__':
    main()