import datetime
import os
import sys


class SyncHandler(object):

    def __init__(self, db, person, splitwise, fixer):
        self.db = db
        self.person = person
        self.splitwise = splitwise
        self.fixer = fixer

        self.nbr_of_updates = 0
        self.nbr_of_deletes = 0
        self.nbr_of_conversions = 0

    def _reset_counters(self):
        self.nbr_of_updates = 0
        self.nbr_of_deletes = 0
        self.nbr_of_conversions = 0

    def _handle_currency_conversion(self, expense):
        if expense.currency != self.person.default_currency:
            for_date = expense.created_at.date()
            from_currency = expense.original_currency
            to_currency = self.person.default_currency
            rate = self.db.get_currency_conversion_rate(
                for_date=for_date,
                from_currency=from_currency,
                to_currency=to_currency
            )
            if rate is None:
                rate = self.fixer.get_conversion_rate(
                    for_date=for_date,
                    from_currency=from_currency,
                    to_currency=to_currency
                )
                self.db.add_currency_conversion(
                    for_date=for_date,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=rate
                )
            expense.cost = round(expense.cost * rate, 2)
            expense.currency = to_currency
            self.nbr_of_conversions += 1
            return expense
        else:
            return expense

    def execute(self):
        self._reset_counters()

        time_previous_sync = self.db.get_last_successful_marker_datetime(self.person.user_id)
        time_now = datetime.datetime.now()

        try:
            new_expenses, deleted_expenses = self.splitwise.get_expenses(time_previous_sync)
            for new_expense in new_expenses:
                new_expense = self._handle_currency_conversion(new_expense)
                self.db.session.merge(new_expense)
                self.nbr_of_updates += 1
                self.db.session.commit()
            for deleted_expense_id in deleted_expenses:
                self.db.delete_expense_by_id(expense_id=deleted_expense_id)
                self.nbr_of_deletes += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            message = "(%s:%s) %s: %s" % (fname, exc_tb.tb_lineno, exc_type, e)
            self.db.add_marker(
                user_id=self.person.user_id,
                created_at=time_now,
                success=False,
                nbr_of_updates=self.nbr_of_updates,
                nbr_of_deletes=self.nbr_of_deletes,
                nbr_of_conversions=self.nbr_of_conversions,
                message=message
            )
        else:
            self.db.add_marker(
                user_id=self.person.user_id,
                created_at=time_now,
                success=True,
                nbr_of_updates=self.nbr_of_updates,
                nbr_of_deletes=self.nbr_of_deletes,
                nbr_of_conversions=self.nbr_of_conversions,
                message=None
            )