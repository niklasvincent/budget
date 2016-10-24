import json
import os
import sys
import unittest

from datetime import date

from mock import Mock, MagicMock


path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../budget'))
sys.path.insert(1, path)


from fixer import Fixer


class TestFixer(unittest.TestCase):

    def _load_file_content(self, filename):
        absolute_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
        with open(absolute_filename, 'r') as f:
            data = f.read()
        return data

    def setUp(self):
        self.fixer = Fixer()

    def testValidateCurrency(self):
        self.assertTrue(
            self.fixer._validate_currency("EUR"),
            "EUR should be a valid known currency"
        )
        self.assertTrue(
            self.fixer._validate_currency("GBP"),
            "GBP should be a valid known currency"
        )
        self.assertTrue(
            self.fixer._validate_currency("DKK"),
            "DKK should be a valid known currency"
        )
        self.assertTrue(
            self.fixer._validate_currency("SEK"),
            "SEK should be a valid known currency"
        )
        self.assertFalse(
            self.fixer._validate_currency("JSP"),
            "JSP should not be a valid known currency"
        )
        self.assertFalse(
            self.fixer._validate_currency("RYU"),
            "RYU should not be a valid known currency"
        )

    def testCurrencyConversionWithSameCurrency(self):
        self.assertEquals(
            self.fixer.get_conversion_rate(
                for_date=date(2015, 4, 18),
                from_currency="GBP",
                to_currency="GBP"
            ),
            1.0,
            "Conversion rate for same currency should be 1.0"
        )
        self.assertEquals(
            self.fixer.get_conversion_rate(
                for_date=date(2015, 6, 18),
                from_currency="EUR",
                to_currency="EUR"
            ),
            1.0,
            "Conversion rate for same currency should be 1.0"
        )

    def testCurrencyConversion(self):
        conversions = {
            "2016-10-14": self._load_file_content("data/currency/2016-10-14.json"),
            "2016-10-21": self._load_file_content("data/currency/2016-10-21.json")
        }
        m = Mock()

        requested_urls = []

        def mock_request(url):
            requested_urls.append(url)
            if url.endswith("2016-10-14"):
                return conversions["2016-10-14"]
            if url.endswith("2016-10-21"):
                return conversions["2016-10-21"]

        m.side_effect = mock_request

        self.fixer._request = m

        sek_rate = self.fixer.get_conversion_rate(
            for_date=date(2016, 10, 14),
            from_currency="SEK",
            to_currency="GBP"
        )
        self.assertEquals(
            sek_rate,
            0.09
        )
        self.assertEquals(
            requested_urls[0],
            "http://api.fixer.io/2016-10-14"
        )

        eur_rate = self.fixer.get_conversion_rate(
            for_date=date(2016, 10, 21),
            from_currency="EUR",
            to_currency="GBP"
        )
        self.assertEquals(
            eur_rate,
            0.89
        )
        self.assertEquals(
            requested_urls[1],
            "http://api.fixer.io/2016-10-21"
        )

def main():
    unittest.main()

if __name__ == '__main__':
    main()