#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import unittest

from kbart.kbart import Kbart
from kbart.exceptions import ProviderNotFound, UnknownEmbargoFormat, InvalidRP


# run 'python -m test.test_kbart' for test cases to properly run
class TestKbart(unittest.TestCase):
    """Tests defining behavior of a new Kbart class."""

    def setUp(self):
        # Fewer fields defined than exist in an RP2 Kbart file,
        # will define the undefined fields as empty string
        self._data_with_holdings = ('My Journal', '1111-2222', '1111-2222',
                                    '2015-01-01', '1', '1', '2016-01-01', '2',
                                    '2', 'http://www.example.com', '', '', '',
                                    '', '', '', 'My Publisher', 'journal')
        self._data_with_embargo = ('My Journal', '1111-2222', '1111-2222',
                                   '', '', '', '', '',  '',
                                   'http://www.example.com', '', '', 'R1Y',
                                   '', '', '', 'My Publisher', 'journal')

        self.kbart = Kbart(self._data_with_holdings)
        self.kbart_embargo = Kbart(self._data_with_embargo)

    def test_invalid_rp(self):
        with self.assertRaises(InvalidRP):
            Kbart(rp=3)

    def test_valid_rp(self):
        rp1_kbart = Kbart(rp=1)
        last_key = rp1_kbart.fields[-1]
        self.assertEqual(last_key, 'coverage_notes')

    def test_unsupported_provider(self):
        with self.assertRaises(ProviderNotFound):
            Kbart(provider='Myself')

    def test_supported_provider(self):
        oclc_kbart = Kbart(provider='oclc')
        last_key = oclc_kbart.fields[-1]
        self.assertEqual(last_key, 'ACTION')

    def test_title(self):
        self.assertEqual(self.kbart.title, 'My Journal')

    def test_holdings_pretty_print(self):
        correct_holdings = 'Volume: 1, Issue: 1, 2015-01-01 - Volume: 2, Issue: 2, 2016-01-01'
        self.assertEqual(correct_holdings, self.kbart.serial_holdings_pp())

    def test_embargo_pretty_print(self):
        correct_embargo = 'From 1 year(s) ago to present'
        self.assertEqual(correct_embargo, self.kbart_embargo.embargo_pp())

    def test_embargo_set(self):
        embargoed = Kbart(self._data_with_embargo)
        embargoed.embargo = 'P1M'
        new_embargo = 'Up to 1 month(s) ago'
        self.assertEqual(new_embargo, embargoed.embargo_pp())

        with self.assertRaises(UnknownEmbargoFormat):
            embargoed.embargo = 'Z32L'  # Any string not like an embargo


if __name__ == '__main__':
    unittest.main()
