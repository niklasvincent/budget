import argparse
import logging
import sys
import time


from budget.aggregator import Aggregator
from budget.config import Config
from budget.database import *
from budget.fixer import Fixer
from budget.slack import Slack
from budget.splitwise import Splitwise
from budget.sync_handler import SyncHandler


import requests
import schedule
from raven import Client


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
        "--config",
        required=True,
        help="Configuration path or S3 URL",
    )
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
    args_parser.add_argument(
        "--periodic",
        help="Perform periodic sync of expenses from Splitwise",
        action="store_true"
    )
    args = args_parser.parse_args()
    return args


def set_up(args):
    config = Config(args.config)
    db = Database(config.get_database_uri())
    db.create_tables()

    aggregator = Aggregator(db)
    slack = Slack(
        people=config.get_people(),
        slack_config=config.get_slack_config(),
        aggregator=aggregator
    )

    fixer = Fixer()

    logger = get_logger(args.debug)

    return config, db, slack, fixer, logger


def main():
    args = parse_arguments()

    config, db, slack, fixer, logger = set_up(args)
    sentry_client = Client(config.sentry_url)

    def report_success():
        """Report successful run to healthchecks.io"""
        if not args.debug:
            requests.get(config.healthchecks_url)

    def purge_expenses():
        logger.info("Asked to purge all expenses in database")
        nbr_of_purged_records = db.purge_expenses()
        logger.info("%d expenses purged" % nbr_of_purged_records)

    def purge_markers():
        logger.info("Asked to purge all markers in database")
        nbr_of_purged_records = db.purge_markers()
        logger.info("%d markers purged" % nbr_of_purged_records)

    def purge_all():
        purge_expenses()
        purge_markers()

    def sync_expenses():
        logger.info("Starting sync with Splitwise")
        for person in config.get_people():
            logger.info("Syncing for user %s" % person.name)
            splitwise = Splitwise(config.get_splitwise_consumer(), person)
            sync_handler = SyncHandler(
                db=db,
                person=person,
                splitwise=splitwise,
                fixer=fixer
            )

            sync_handler.execute(sentry_client)

            last_marker = db.get_last_marker(user_id=person.user_id)

            if not last_marker.success:
                logger.error("Sync for user %s failed: %s" % (person.name, last_marker.message))
                last_successful_marker = db.get_last_successful_marker(user_id=person.user_id)
                logger.info(
                    "Last successful sync for user %s was at %s" % (person.name, last_successful_marker.created_at)
                )
            else:
                report_success()
                logger.info("Sync for user %s successful" % person.name)
                logger.info(
                    "%d record(s) added/updated, %d record(s) deleted, %d currency conversion(s) performed" %
                    (last_marker.nbr_of_updates, last_marker.nbr_of_deletes, last_marker.nbr_of_conversions)
                )

    def slack_notifications():
        for person in config.get_people():
            last_marker = db.get_last_marker(user_id=person.user_id)
            slack.notify(last_marker=last_marker, person=person)

    if args.purge_expenses:
        purge_expenses()

    if args.purge_markers:
        purge_markers()

    if args.sync and not args.periodic:
        sync_expenses()

    if args.periodic:
        try:
            logger.info("Scheduling periodic jobs")

            for person in config.get_people():
                logger.info("Configured to sync for: %s", person.name)

            # Purge and sync after just starting up
            purge_all()
            sync_expenses()

            schedule.every(15).minutes.do(sync_expenses)
            schedule.every().monday.do(purge_all)

            # Schedule Slack notifications
            for moment in config.get_slack_config().schedule:
                schedule.every().day.at(moment).do(slack_notifications)

            # Send off initial Slack notification when starting up
            slack_notifications()

            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception:
            sentry_client.captureException()

if __name__ == '__main__':
    main()
