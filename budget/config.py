import yaml


import oauth2


class Person(object):

    def __init__(self, name, user_id, default_currency, access_token, access_secret):
        self.name = name
        self.user_id = user_id
        self.default_currency = default_currency
        self.token = oauth2.Token(access_token, access_secret)


class Config(object):

    def __init__(self, config_filename):
        self.data = self._load_config(config_filename)
        assert self.data != None, "Got no data from configuration file %s" % config_filename
        assert self.data.get("splitwise") != None, "Configuration file %s does not have a splitwise section" %\
                                                   config_filename

    def _load_config(self, config_filename):
        with open(config_filename) as f:
            return yaml.load(f)

    def get_database_uri(self):
        return self.data["database"]["uri"]

    def get_splitwise_consumer(self):
        return oauth2.Consumer(
            self.data["splitwise"]["consumer_key"],
            self.data["splitwise"]["consumer_secret"]
        )

    def get_people(self):
        people = []
        for person in self.data.get("splitwise").get("people"):
            people.append(Person(
                name=person["name"],
                user_id=person["user_id"],
                default_currency=person["default_currency"],
                access_token=person["access_token"],
                access_secret=person["access_secret"]
                )
            )
        return people