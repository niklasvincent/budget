import json
import urllib
from collections import namedtuple
from datetime import datetime

import dateutil.parser
import oauth2

from database import Expense

Category = namedtuple("Category", ["id", "name", "parent"])


class Splitwise(object):

    def __init__(self, consumer, person):
        self.base_url = 'https://secure.splitwise.com/api/v3.0'
        self.client = oauth2.Client(consumer, person.token)
        self.person = person

    def request(self, url, method ="GET"):
        """Make HTTP request and deserialise the JSON response"""
        resp, content = self.client.request(url, method)
        return json.loads(content)

    def _build_url(self, path, query = dict()):
        """Build a full URL using the relative URL"""
        query_string = urllib.urlencode(query) if query else ""
        return "%s/%s?%s" % (self.base_url, path, query_string)

    def _parse_date(self, date):
        """Parse date from string, ignoring timezone"""
        return dateutil.parser.parse(date, ignoretz=True)

    def _get_user_share(self, expense):
        """Get the proportional share for the user ID as part of this expense"""
        users = set([user["user"]["id"] for user in expense["users"]])
        if self.person.user_id in users:
            owed_share = [user.get("owed_share", 0) for user in expense["users"] if user["user"]["id"] == self.person.user_id][0]
            if owed_share is not None:
                return float(owed_share)
        return 0

    def _get_group_id(self, expense):
        if expense.get("group_id") is None:
            return 0
        return int(expense.get("group_id"))

    def _is_applicable_expense(self, expense):
        """Check whether expense is applicable to the current user"""
        if expense.get("deleted_by") or expense.get("creation_method") in ["debt_consolidation", "payment"]:
            return False
        user_share = self._get_user_share(expense)
        return user_share > 0

    def get_expenses(self, updated_after=None):
        """Get all expenses"""
        # TODO: What to do with deleted?! Return separate list?
        url_parameters = {"limit": "0"}
        if updated_after is not None and isinstance(updated_after, datetime):
            url_parameters = {"updated_after" : updated_after.isoformat()}

        categories = self.get_categories()

        raw_expenses = self.request(self._build_url("get_expenses", url_parameters)).get("expenses")
        processed_expenses = []

        for e in filter(self._is_applicable_expense, raw_expenses):
            id = int("".join([str(self.person.user_id), str(e.get("id"))]))
            user_id = int(self.person.user_id)
            created_at = self._parse_date(e.get("date"))
            description = e.get("description").strip()
            category = categories.get(e.get("category").get("id"))
            parent_category = category.parent
            child_category = category.name
            user_share = self._get_user_share(e)
            group_id = self._get_group_id(e)
            currency = e.get("currency_code")

            expense = Expense(
                id=id,
                user_id=user_id,
                group_id=group_id,
                created_at=created_at,
                description=description,
                parent_category=parent_category,
                child_category=child_category,
                cost=user_share,
                currency=currency,
                original_currency=currency
            )

            processed_expenses.append(expense)
        return processed_expenses

    def get_categories(self):
        """Get all categories"""
        categories = {}
        for subcategories in self.request(self._build_url("get_categories", {})).get("categories"):
            subcategories = subcategories.get("subcategories")
            for subcategory in subcategories:
                category = Category(
                    subcategory.get("id"),
                    subcategory.get("name"),
                    subcategory.get("icon").split("/")[-2:][0].capitalize()
                )
                categories[subcategory.get("id")] = category
        return categories
