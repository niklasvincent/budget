import json
import time
import urllib2


class FixerException(Exception):
    pass


class Fixer(object):

    def __init__(self):
        self.base_url = "http://api.fixer.io/"
        self.known_currencies = {
            u'USD',
            u'IDR',
            u'BGN',
            u'ILS',
            u'GBP',
            u'DKK',
            u'CAD',
            u'JPY',
            u'HUF',
            u'RON',
            u'MYR',
            u'SEK',
            u'SGD',
            u'HKD',
            u'AUD',
            u'CHF',
            u'KRW',
            u'CNY',
            u'TRY',
            u'HRK',
            u'NZD',
            u'THB',
            u'NOK',
            u'RUB',
            u'INR',
            u'MXN',
            u'CZK',
            u'BRL',
            u'PLN',
            u'PHP',
            u'ZAR'
        }

    @classmethod
    def _request(self, url):
        """Retrieve from API"""
        try:
            req = urllib2.Request(url=url)
            f = urllib2.urlopen(req)
            return f.read()
        except Exception as e:
            raise FixerException("Could not convert currency, url=%s: %s" % (url, e))

    def _conversionsForDate(self, date):
        """Retrieve currency conversions for date"""
        query_url = self.base_url + date.isoformat()
        content = self._request(query_url)
        return json.loads(content)

    def _validate_currency(self, currency):
        return currency == 'EUR' or currency in self.known_currencies

    def get_conversion_rate(self, for_date, from_currency, to_currency):
        """Convert from one currency to the other, at a specific point in time, if necessary"""
        for currency in [from_currency, to_currency]:
            if not self._validate_currency(currency):
                raise FixerException("Not a known currency: %s" % currency)

        if from_currency == to_currency:
            return 1.0

        exchange_rates = self._conversionsForDate(for_date)

        # Since EUR is the base currency, we need to do this slightly different for any EUR requests
        if from_currency == 'EUR':
            conversion_rate = float(exchange_rates['rates'][to_currency])
        else:
            previous_currency_rate = float(exchange_rates['rates'][from_currency])
            new_currency_rate = float(exchange_rates['rates'][to_currency])
            conversion_rate = new_currency_rate/previous_currency_rate

        return round(conversion_rate, 2)