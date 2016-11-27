import os
import sys
import unittest

from datetime import date, datetime

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../budget'))
sys.path.insert(1, path)

from aggregator import *
from database import *


class TestAggregator(unittest.TestCase):

    def setUp(self):
        self.db = Database("sqlite:///:memory:")
        self.db.create_tables()

    def testMonthRange(self):
        aggregator = Aggregator(self.db)
        first, last = aggregator._range_for_month(2016, 10)
        self.assertEquals(
            first,
            date(2016, 10, 1)
        )
        self.assertEquals(
            last,
            date(2016, 10, 31)
        )


def main():
    unittest.main()

if __name__ == '__main__':
    main()