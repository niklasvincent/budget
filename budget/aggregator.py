import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta


from database import *


class Aggregator(object):

    def __init__(self, db):
        self.db = db

    @classmethod
    def _range_for_month(self, year, month):
        _, last_day = calendar.monthrange(year, month)
        return date(year, month, 1), date(year, month, last_day)

    def _range_for_this_month(self):
        now = datetime.now()
        return self._range_for_month(now.year, now.month)

    def get_expenses_for_month(self, person, year, month):
        first_day, last_day = self._range_for_month(year, month)
        expenses_by_group = defaultdict(list)
        total_sum_by_group = defaultdict(int)
        total_sum = 0
        for expense in self.db.get_expenses_between(person.user_id, first_day, last_day):
            expenses_by_group[expense.group].append(expense.as_dictionary())
            total_sum_by_group[expense.group] += expense.cost
            total_sum += expense.cost
        for group in total_sum_by_group.iterkeys():
            total_sum_by_group[group] = '%.2f' % round(total_sum_by_group[group], 2)
        total_sum = '%.2f' % round(total_sum, 2)
        return {
            "expenses_by_group": expenses_by_group,
            "total_sum_by_group": total_sum_by_group,
            "total_sum": total_sum
        }

    def get_expenses_for_this_month(self, person):
        now = datetime.now()
        return self.get_expenses_for_month(person, now.year, now.month)