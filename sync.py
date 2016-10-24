import datetime

from budget.config import Config
from budget.database import *
from budget.splitwise import Splitwise


def main(config_filename):
    config = Config(config_filename)
    db = Database(config.get_database_uri())
    db.create_tables()

    for person in config.get_people():
        splitwise = Splitwise(config.get_splitwise_consumer(), person)


        time_previous_sync = db.get_last_successful_marker_datetime(person.user_id)
        time_now = datetime.datetime.now()

        try:
            expenses = splitwise.get_expenses(time_previous_sync)
            for expense in expenses:
                db.session.merge(expense)
                db.session.commit()
        except Exception as e:
            db.add_marker(
                user_id=person.user_id,
                created_at=time_now,
                success=False,
                nbr_of_updates=0,
                nbr_of_deletes=0,
                message=str(e)
            )
        else:
            nbr_of_updates = len(expenses)
            db.add_marker(
                user_id=person.user_id,
                created_at=time_now,
                success=True,
                nbr_of_updates=nbr_of_updates,
                nbr_of_deletes=0,
                message=None
            )


if __name__ == '__main__':
    main("/etc/budget.conf")
