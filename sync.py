import datetime
import sys

from budget.database import *
from budget.config import Config
from budget.splitwise import Splitwise


def main(config_filename):
    config = Config(config_filename)
    db = Database(config.get_database_uri())
    db.create_tables()

    for person in config.get_people():
        splitwise = Splitwise(config.get_splitwise_consumer(), person)
        expenses = splitwise.get_expenses()
        for expense in expenses:
            db.session.merge(expense)
            db.session.commit()


if __name__ == '__main__':
    main("/etc/budget.conf")
