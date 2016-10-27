import yaml


import oauth2


class Person(object):

    def __init__(self, name, user_id, email_address, default_currency, access_token, access_secret):
        self.name = name
        self.user_id = user_id
        self.email_address = email_address
        self.default_currency = default_currency
        self.token = oauth2.Token(access_token, access_secret)
        self.is_active = True

    def get_id(self):
        return self.email_address


class Config(object):

    def __init__(self, config_filename):
        self.data = self._load_config(config_filename)
        assert self.data != None, "Got no data from configuration file %s" % config_filename
        assert self.data.get("splitwise") != None, "Configuration file %s does not have a splitwise section" %\
                                                   config_filename
        self.users = {}
        self._populate_user_lookup()

    def _load_config(self, config_filename):
        with open(config_filename) as f:
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

    def get_people(self):
        people = []
        for person in self.data.get("splitwise").get("people"):
            full_person = Person(
                name=person["name"],
                user_id=person["user_id"],
                email_address=person["email_address"],
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
