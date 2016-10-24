import argparse
import logging
import sys

from budget.config import Config
from budget.database import *
from budget.fixer import Fixer
from budget.splitwise import Splitwise
from budget.sync_handler import SyncHandler


def get_logger(debug=False):
    root = logging.getLogger()
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - sync - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    if debug:
        ch.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
        root.setLevel(logging.INFO)
    return logging


def parse_arguments():
    # Parse command line arguments
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--debug",
        help="Increase verbosity",
        action="store_true"
    )
    args_parser.add_argument(
        "--purge-expenses",
        help="Purge expenses from database",
        action="store_true"
    )
    args_parser.add_argument(
        "--purge-markers",
        help="Purge markers from database",
        action="store_true"
    )
    args_parser.add_argument(
        "--sync",
        help="Perform sync of expenses from Splitwise",
        action="store_true"
    )
    args = args_parser.parse_args()
    return args


def main(config_filename):
    args = parse_arguments()

    config = Config(config_filename)
    db = Database(config.get_database_uri())
    db.create_tables()

    fixer = Fixer()

    logging = get_logger(args.debug)

    if args.purge_expenses:
        logging.info("Asked to purge all expenses in database")
        nbr_of_purged_records = db.purge_expenses()
        logging.info("%d expenses purged" % nbr_of_purged_records)
        sys.exit(0)

    if args.purge_markers:
        logging.info("Asked to purge all markers in database")
        nbr_of_purged_records = db.purge_markers()
        logging.info("%d markers purged" % nbr_of_purged_records)
        sys.exit(0)

    if args.sync:
        logging.info("Starting sync with Splitwise")
        for person in config.get_people():
            logging.info("Syncing for user %s" % person.name)
            splitwise = Splitwise(config.get_splitwise_consumer(), person)
            sync_handler = SyncHandler(
                db=db,
                person=person,
                splitwise=splitwise,
                fixer=fixer
            )

            sync_handler.execute()

            last_marker = db.get_last_marker(user_id=person.user_id)

            if not last_marker.success:
                logging.error("Sync for user %s failed: %s" % (person.name, last_marker.message))
                last_successful_marker = db.get_last_successful_marker(user_id=person.user_id)
                logging.info(
                    "Last successful sync for user %s was at %s" % (person.name, last_successful_marker.created_at)
                )
            else:
                logging.info("Sync for user %s successful" % person.name)
                logging.info(
                    "%d records added/updated, %d records deleted, %d currency conversions performed" %
                    (last_marker.nbr_of_updates, last_marker.nbr_of_deletes, last_marker.nbr_of_conversions)
                )
        sys.exit(0)


if __name__ == '__main__':
    main("/etc/budget.conf")
