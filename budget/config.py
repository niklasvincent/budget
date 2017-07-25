import sys
from collections import defaultdict
from urlparse import urlparse


import yaml


import boto3
import oauth2


class SlackConfig(object):

    def __init__(self, slack_config_data):
        self.access_token = slack_config_data["access_token"]
        self.schedule = slack_config_data["when"]
        self.channel_name = slack_config_data["channel"]
        self.bot_username = slack_config_data["name"]
        self.icon_url = slack_config_data["icon_url"]
        self.schedule = slack_config_data["when"]


class Person(object):

    def __init__(self, name, user_id, email_address, groups, default_currency, access_token, access_secret):
        self.name = name
        self.user_id = user_id
        self.email_address = email_address
        self.groups = groups
        self.default_currency = default_currency
        self.token = oauth2.Token(access_token, access_secret)
        self.is_active = True

    def get_id(self):
        return self.email_address


class Config(object):

    def __init__(self, config_url):
        self.data = self._load_config(config_url)
        assert self.data != None, "Got no data from configuration file %s" % config_url
        assert self.data.get("splitwise") != None, "Configuration file %s does not have a splitwise section" % \
                                                   config_url

        self.users = {}
        self._populate_user_lookup()
        self.pre_authenticated_user = None

    @classmethod
    def _load_config(self, config_url):
        try:
            url = urlparse(config_url)
        except Exception as e:
            print "Could not parse config URL '%s': %s" % (config_url, e)
            sys.exit(1)

        if url.scheme == "s3":
            session = boto3.Session()
            s3 = session.client('s3')
            bucket = url.netloc
            key = url.path[1:]
            response = s3.get_object(
                Bucket=bucket,
                Key=key
            )
            return yaml.load(response['Body'].read().decode('utf-8'))
        else:
            with open(url.path) as f:
                return yaml.load(f)

    def _populate_user_lookup(self):
        for person in self.get_people():
            self.users[person.email_address] = person

    def get_database_uri(self):
        return self.data["database"]["uri"]

    def get_splitwise_consumer(self):
        return oauth2.Consumer(
            self.data["splitwise"]["consumer_key"],
            self.data["splitwise"]["consumer_secret"]
        )

    @classmethod
    def _get_groups_for_person(self, person):
        default_group = [group for group in person.get("groups") if group.get("default")][0]["default"]
        groups = defaultdict(lambda: default_group)
        for group in person["groups"]:
            if group.items()[0][0] != "default":
                groups.update(group)
        return groups

    def get_people(self):
        people = []
        for person in self.data.get("splitwise").get("people"):
            groups = self._get_groups_for_person(person)
            full_person = Person(
                name=person["name"],
                user_id=person["user_id"],
                email_address=person["email_address"],
                groups=groups,
                default_currency=person["default_currency"],
                access_token=person["access_token"],
                access_secret=person["access_secret"]
            )
            people.append(full_person)
        return people

    def get_google_auth_credentials(self):
        return self.data["google_auth"]["client_id"], self.data["google_auth"]["client_secret"]

    def get_user_by_email(self, email):
        return self.users.get(email, None)

    def get_slack_config(self):
        return SlackConfig(self.data["slack"])

    @property
    def healthchecks_url(self):
        return self.data["monitoring"]["healthchecks_url"]

    @property
    def sentry_url(self):
        return self.data["monitoring"]["sentry_url"]
