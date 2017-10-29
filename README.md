[![Build Status](https://travis-ci.org/nlindblad/budget.svg?branch=master)](https://travis-ci.org/nlindblad/budget) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/bdb721784c2e4019a2938dae87a2d6a3)](https://www.codacy.com/app/niklas/budget?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nlindblad/budget&amp;utm_campaign=Badge_Grade)
# Budget

1. Syncs [Splitwise](https://splitwise.com) into a SQL database (SQLite, but pluggable thanks to SQLAlchemy). Uses [Fixer.io](https://fixer.io) for currency conversions.
2. Web interface (with authentication using Google OAuth) with spend breakdown for each month
3. Slack bot posting current monthly spend

## Run

### Docker

The lastest Docker image is available at [Docker Hub](https://hub.docker.com/r/nlindblad/budget/).

If you are building locally, simply run `make docker`

### Virtualenv

Install all requirements by running `make virtualenv`

Start each of `web.py` and `sync.py` (don't forget to source the virtualenv `. ./venv/bin/activate`).

## Configuration

### Environment

Make sure the following environment variables are set:

```
AWS_DEFAULT_REGION=eu-west-1
AWS_ACCESS_KEY_ID=XXXXXX
AWS_SECRET_ACCESS_KEY=YYYYYYY
CONFIG_URL=s3://bucket/config.yml
```

### Configuration file

The configuration file in S3 in on the format:

```
---

splitwise:
  consumer_key: "XXXXX" # Set up a new Splitwise OAuth application to retrieve this
  consumer_secret: "YYYYY" # Set up a new Splitwise OAuth application to retrieve this
  people:
    - name: "Niklas"
      email_address: "XXXXX"
      access_token: "XXXXXX"
      access_secret: "XXXXXX"
      user_id: 1234
      default_currency: GBP
      groups:
        - 123: "Alias for group"
        - default: "Day to Day Expenses"
      currencies:
        - SEK
    - name: "Iona"
      email_address: "XXXXX"
      access_token: "XXXXXX"
      access_secret: "XXXXXX"
      user_id: 12345
      default_currency: GBP
      groups:
        - 1234: "Alias for group"
        - default: "Day to Day Expenses"

database:
  uri: sqlite:///budget.db

slack:
  access_token: "XXXXXX"
  channel: "#channel"
  name: "budget"
  icon_url: "https://pbs.twimg.com/profile_images/626832022061875200/rAK0SMIW.jpg"
  when:
    - "09:00"
    - "13:00"
    - "20:00"

monitoring:
  sentry_url: "https://xxx:yyyy@sentry.io/1234"
  healthchecks_url: "https://hchk.io/xxxzzz"

google_auth:
  client_id: "xxxxx" # Set up a new Google OAuth application to retrieve this
  client_secret: "yyyy" # Set up a new Google OAuth application to retrieve this
```

### External services used

1. [Splitwise](http://dev.splitwise.com/)
2. [Google OAuth](https://developers.google.com/identity/sign-in/web/devconsole-project)
3. [Slack](https://api.slack.com/slack-apps)
4. [Sentry](https://sentry.io/welcome/)
5. [Healthchecks.io](https://healthchecks.io/)




