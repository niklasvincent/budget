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
        db.session.add(
            Expense(
                id=1,
                user_id=2,
                created_at=datetime(2016, 10, 22),
                description='Some description',
                parent_category='Life',
                child_category='Groceries',
                cost=50.33,
                currency='GBP',
                original_currency='SEK'
            )
        )

        db.session.commit()
        expense = db.session.query(Expense).filter_by(id=1).first()
        self.assertEquals(
            expense.id,
            1,
            'Wrong expense ID'
        )
        self.assertEquals(
            expense.user_id,
            2,
            'Wrong user ID'
        )
        self.assertEquals(
            expense.created_at,
            datetime(2016, 10, 22),
            'Wrong creation time'
        )
        self.assertEquals(
            expense.description,
            'Some description',
            'Wrong description'
        )
        self.assertEquals(
            expense.parent_category,
            'Life',
            'Wrong parent category'
        )
        self.assertEquals(
            expense.child_category,
            'Groceries',
            'Wrong child category'
        )
        self.assertEquals(
            expense.cost,
            50.33,
            'Wrong cost'
        )
        self.assertEquals(
            expense.currency,
            'GBP',
            'Wrong currency'
        )
        self.assertEquals(
            expense.original_currency,
            'SEK',
            'Wrong original currency'
        )

    def testMarker(self):
        db = Database("sqlite:///:memory:")
        db.create_tables()
        db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 5, 0),
            user_id=1234,
            success=True,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 6, 0),
            user_id=1234,
            success=False,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 6, 0),
            user_id=4567,
            success=False,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 6, 0),
            user_id=4567,
            success=True,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 7, 0),
            user_id=1234,
            success=False,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 8, 0),
            user_id=1234,
            success=True,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        db.add_marker(
            created_at=datetime(2016, 10, 22, 12, 9, 0),
            user_id=1234,
            success=False,
            nbr_of_deletes=0,
            nbr_of_updates=10,
            nbr_of_conversions=2,
            message=None
        )
        marker = db.get_last_successful_marker(1234)
        self.assertEquals(
            marker.created_at,
            datetime(2016, 10, 22, 12, 8, 0),
            'Wrong timestamp'
        )
        self.assertEquals(
            db.get_last_successful_marker_datetime(1234),
            datetime(2016, 10, 22, 12, 8, 0),
            'Wrong timestamp'
        )
        self.assertEquals(
            marker.success,
            True,
            'Not successful'
        )


def main():
    unittest.main()

if __name__ == '__main__':
    main()