import calendar
from collections import defaultdict, namedtuple, OrderedDict
from datetime import date, datetime
from operator import itemgetter

from database import *


class Aggregator(object):
    def __init__(self, db):
        self.db = db

    @classmethod
    def _range_for_month(self, year, month):
        _, last_day = calendar.monthrange(year, month)
        return date(year, month, 1), date(year, month, last_day)

    @staticmethod
    def _range_for_this_month(self):
        now = datetime.now()
        return self._range_for_month(now.year, now.month)

    @staticmethod
    def _round_dict_values(dictionary, decimal_places):
        for key in dictionary.iterkeys():
            if isinstance(dictionary[key], dict):
                dictionary[key] = Aggregator._round_dict_values(dictionary[key], decimal_places)
            else:
                dictionary[key] = float('%.2f' % round(dictionary[key], decimal_places))
        return dictionary

    @staticmethod
    def _friendly_name(name):
        parent, child = name.split('/', 1)
        if child == "Other":
            return "{} {}".format(child, parent)
        return child

    @staticmethod
    def _sorted_by_dict_value(dictionary):
        return OrderedDict(sorted(dictionary.items(), key=itemgetter(1), reverse=True))

    def get_expenses_for_month(self, person, year, month):
        first_day, last_day = self._range_for_month(year, month)
        expenses_by_group = defaultdict(lambda: defaultdict(list))
        total_sum_by_group = defaultdict(int)
        total_sum_by_category = defaultdict(lambda: defaultdict(float))
        total_sum = 0

        for expense in self.db.get_expenses_between(person.user_id, first_day, last_day):
            expenses_by_group[expense.group][expense.category].append(expense.as_dictionary())
            total_sum_by_group[expense.group] += expense.cost
            total_sum_by_category[expense.group][expense.category] += expense.cost
            total_sum += expense.cost

        # Round to two decimal places
        total_sum_by_group = self._round_dict_values(total_sum_by_group, 2)
        total_sum_by_category = self._round_dict_values(total_sum_by_category, 2)
        total_sum = float('%.2f' % round(total_sum, 2))

        for group in total_sum_by_category.iterkeys():
            sorted_total_sum_by_category = self._sorted_by_dict_value(total_sum_by_category[group])
            total_sum_by_category_for_group = []
            for category, total_sum_for_category in sorted_total_sum_by_category.items():
                total_sum_by_category_for_group.append({
                    "name": self._friendly_name(category),
                    "total_sum": total_sum_for_category,
                    "expenses": expenses_by_group[group][category]
                })
            total_sum_by_category[group] = total_sum_by_category_for_group

        return {
            "total_sum_by_group": total_sum_by_group,
            "total_sum_by_category": total_sum_by_category,
            "total_sum": total_sum
        }

    def get_expenses_for_this_month(self, person):
        now = datetime.now()
        return self.get_expenses_for_month(person, now.year, now.month)
