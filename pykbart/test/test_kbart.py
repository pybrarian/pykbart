#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import datetime
import unittest

import pytest

from pykbart.kbart import Kbart, Embargo, Holdings
from pykbart.exceptions import (ProviderNotFound, UnknownEmbargoFormat,
                                InvalidRP, IncompleteDateInformation)


class TestKbart(unittest.TestCase):

    def setUp(self):
        # Fewer fields defined than exist in an RP2 Kbart file,
        # will define the undefined fields as empty string
        self._data = ('My Journal', '1111-2222', '1111-2222',
                      '2015-01-01', '1', '1', '2016-01-01', '2',
                      '2', 'http://www.example.com', '', '', '',
                      '', '', '', 'My Publisher', 'journal')
        self.kbart = Kbart(self._data)

    def test_invalid_rp(self):
        with pytest.raises(InvalidRP):
            Kbart(rp=3)

    def test_valid_rp(self):
        rp1_kbart = Kbart(rp=1)
        last_key = rp1_kbart.fields[-1]
        assert last_key == 'coverage_notes'

    def test_unsupported_provider(self):
        with pytest.raises(ProviderNotFound):
            Kbart(provider='Myself')

    def test_supported_provider(self):
        oclc_kbart = Kbart(provider='oclc')
        last_key = oclc_kbart.fields[-1]
        assert last_key == 'ACTION'

    def test_holdings_pretty_print(self):
        correct_holdings = '2015-01-01, Vol: 1, Issue: 1 - 2016-01-01, Vol: 2, Issue: 2'
        assert correct_holdings == self.kbart.holdings_pp()

    def test_repr_with_no_data_or_fields(self):
        assert repr(Kbart(rp=2)) == 'Kbart(data=[], provider=None, rp=2, fields=[\'publication_title\', \'print_identifier\', \'online_identifier\', \'date_first_issue_online\', \'num_first_vol_online\', \'num_first_issue_online\', ...])'

    def test_repr_with_data_no_fields(self):
        assert repr(self.kbart) == 'Kbart(data=[\'My Journal\', \'1111-2222\', \'1111-2222\', \'2015-01-01\', \'1\', \'1\', ...], provider=None, rp=2, fields=[\'publication_title\', \'print_identifier\', \'online_identifier\', \'date_first_issue_online\', \'num_first_vol_online\', \'num_first_issue_online\', ...])'

    def test_comparing_coverage_ranges(self):
        data = ('My Journal', '1111-2222', '1111-2222', '2014-01-01', '1', '1',
                '2016-01-01', '2', '2', 'http://www.example.com', '', '', '',
                '', '', '', 'My Publisher', 'journal')

        assert self.kbart.compare_coverage(Kbart(data)) == -365


class TestEmbargo(unittest.TestCase):

    def test_pretty_print_valid_embargo_code(self):
        assert Embargo.pretty_print('P1M') == 'Up to 1 month(s) ago'

    def test_pretty_print_with_empty_input(self):
        assert Embargo.pretty_print('') == ''

    def test_pretty_print_with_invalid_embargo_code(self):
        with pytest.raises(UnknownEmbargoFormat):
            Embargo.pretty_print('Z32L')

    def test_embargo_check_for_valid_embargo_code(self):
        assert Embargo.check_embargo_format('P1M') is True

    def test_embargo_check_for_invalid_embargo_code(self):
        assert Embargo.check_embargo_format('Z32L') is False


class TestHoldings(unittest.TestCase):

    def setUp(self):
        self.both_dates = ['2015-01-01', '1', '1', '2016-01-01', '2', '2']
        self.start_date_only = ['2015-01-01', '1', '1', '', '', '']
        self.end_date_only = ['', '', '', '2016-01-01', '2', '2']  # error
        # Mock holdings from only a known point back to test length methods
        fake_today = datetime.date.today() - datetime.timedelta(days=375)
        self.mocked_holdings = [fake_today.strftime('%Y-%m-%d'), '1', '1',
                                '', '', '']

    def test_pretty_print_full_holdings_info(self):
        assert (Holdings.pretty_print(self.both_dates) ==
                '2015-01-01, Vol: 1, Issue: 1 - 2016-01-01, Vol: 2, Issue: 2')

    def test_pretty_print_only_first_set_of_holdings(self):
        assert (Holdings.pretty_print(self.start_date_only) ==
                '2015-01-01, Vol: 1, Issue: 1 - present')

    def test_pretty_print_with_no_holdings(self):
        assert (Holdings.pretty_print(['', '', '', '', '', '']) ==
                'No holdings present')

    def test_holdings_length_with_both_dates(self):
        assert Holdings.length_of_coverage(self.both_dates).days == 365

    def test_holdings_length_pp_with_both_dates(self):
        assert Holdings.length_of_coverage_pp(self.both_dates) == '1 year(s)'

    def test_holdings_length_with_only_start_date(self):
        assert Holdings.length_of_coverage(self.mocked_holdings).days == 375

    def test_holdings_length_with_only_start_date_pp(self):
        assert (Holdings.length_of_coverage_pp(self.mocked_holdings) ==
                '1 year(s), 10 day(s)')

    def test_incomplete_holdings(self):
        with pytest.raises(IncompleteDateInformation):
            Holdings.length_of_coverage(self.end_date_only)


if __name__ == '__main__':
    unittest.main()
