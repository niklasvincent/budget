import os
import sys
import unittest

from datetime import datetime

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../budget'))
sys.path.insert(1, path)

from database import *


class TestDatabase(unittest.TestCase):


    def testCreate(self):
        db = Database("sqlite:///:memory:")
        db.create_tables()
        db.session.add(Expense(id=1, user_id=2, created_at=datetime(2016, 10, 22), description='Some description',
                               category='My Category', cost=50.33))

        db.session.commit()
        expense = db.session.query(Expense).filter_by(id=1).first()
        self.assertEquals(expense.id, 1, 'Wrong expense ID')
        self.assertEquals(expense.user_id, 2, 'Wrong user ID')
        self.assertEquals(expense.created_at, datetime(2016, 10, 22), 'Wrong creation time')
        self.assertEquals(expense.description, 'Some description', 'Wrong description')
        self.assertEquals(expense.category, 'My Category', 'Wrong category')
        self.assertEquals(expense.cost, 50.33, 'Wrong cost')

    def testMarker(self):
        db = Database("sqlite:///:memory:")
        db.create_tables()
        db.add_marker(datetime(2016, 10, 22, 12, 5, 0), True, None)
        db.add_marker(datetime(2016, 10, 22, 12, 6, 0), False, None)
        db.add_marker(datetime(2016, 10, 22, 12, 7, 0), False, None)
        db.add_marker(datetime(2016, 10, 22, 12, 8, 0), True, None)
        db.add_marker(datetime(2016, 10, 22, 12, 9, 0), False, None)
        marker = db.get_last_successful_marker()
        self.assertEquals(marker.created_at, datetime(2016, 10, 22, 12, 8, 0), 'Wrong timestamp')
        self.assertEquals(marker.success, True, 'Not successful')


def main():
    unittest.main()

if __name__ == '__main__':
    main()