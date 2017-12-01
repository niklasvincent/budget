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

        status_color = "good" if last_marker.success else "danger"

        fields = []
        for group_name, group_spend in summary["total_sum_by_group"].iteritems():
            fields.append({
                "title": group_name,
                "value": "{group_spend} {currency}".format(
                    group_spend=group_spend,
                    currency=currency
                ),
                "short": False
            })
        fields.append({
            "title": "Total",
            "value": "{total} {currency}".format(
                total=summary["total_sum"],
                currency=currency
            ),
            "short": False
        })

        print(fields)
        print(summary["total_sum_by_group"])

        attachments = [
            {
                "fallback": "Latest budget sync: {total} {currency}".format(
                    total=summary["total_sum"],
                    currency=currency
                ),
                "color": status_color,
                "author_name": "Monthly spend",
                "title": person.name,
                "fields": fields,
                "footer": "Budget",
                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                "ts": last_marker.created_at.strftime('%s')
            }
        ]

        self.slack_client.chat.post_message(
            username=self.slack_config.bot_username,
            as_user=True,
            channel=self.slack_config.channel_name,
            icon_url=self.slack_config.icon_url,
            attachments=attachments,
            text=":money_with_wings: "
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
