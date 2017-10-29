from slacker import Slacker


import datetime


class Slack(object):

    def __init__(self, people, slack_config, aggregator):
        self.people = people
        self.slack_config = slack_config
        self.slack_client = Slacker(slack_config.access_token)
        self.aggregator = aggregator

    def notify(self, last_marker, person):
        currency = person.default_currency
        summary = self.aggregator.get_expenses_for_this_month(person)
        sync_status = "successful :heavy_check_mark:" if last_marker.success else "failed :("
        text = [
            "*{}*".format(person.name),
            "Last sync at {sync_time} {sync_status}".format(sync_time=last_marker.created_at, sync_status=sync_status)
        ]
        text += [" - {}: {} {}".format(k, v, currency) for k, v in summary["total_sum_by_group"].iteritems()]
        text += ["*Total*: {total} {currency}".format(total=summary["total_sum"], currency=currency)]
        self.slack_client.chat.post_message(
            username=self.slack_config.bot_username,
            as_user=False,
            channel=self.slack_config.channel_name,
            icon_url=self.slack_config.icon_url,
            text="\n".join(text)
        )

    def exchange_rate(self, from_currency, to_currencies, fixer):
        today = datetime.datetime.now().date()
        text = [":chart_with_downwards_trend:"]
        for to_currency in to_currencies:
            exchange_rate = fixer.get_conversion_rate(
                for_date=today,
                from_currency=from_currency,
                to_currency=to_currency
            )
            text.append("{from_currency}/{to_currency} = {exchange_rate}".format(
                from_currency=from_currency,
                to_currency=to_currency,
                exchange_rate=exchange_rate
            ))
        self.slack_client.chat.post_message(
            username=self.slack_config.bot_username,
            as_user=False,
            channel=self.slack_config.channel_name,
            icon_url=self.slack_config.icon_url,
            text="\n".join(text)
        )
