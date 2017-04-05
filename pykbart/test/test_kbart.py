#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import datetime
import unittest

import pytest

from pykbart.kbart import Kbart, Holdings
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
        assert correct_holdings == self.kbart.holdings.pretty_print()

    def test_repr_with_no_data_or_fields(self):
        assert repr(Kbart(rp=2)) == 'Kbart(data=[], provider=None, rp=2, fields=[\'publication_title\', \'print_identifier\', \'online_identifier\', \'date_first_issue_online\', \'num_first_vol_online\', \'num_first_issue_online\', ...])'

    def test_repr_with_data_no_fields(self):
        assert repr(self.kbart) == 'Kbart(data=[\'My Journal\', \'1111-2222\', \'1111-2222\', \'2015-01-01\', \'1\', \'1\', ...], provider=None, rp=2, fields=[\'publication_title\', \'print_identifier\', \'online_identifier\', \'date_first_issue_online\', \'num_first_vol_online\', \'num_first_issue_online\', ...])'

    def test_comparing_coverage_ranges(self):
        data = ('My Journal', '1111-2222', '1111-2222', '2014-01-01', '1', '1',
                '2016-01-01', '2', '2', 'http://www.example.com', '', '', '',
                '', '', '', 'My Publisher', 'journal')
        assert self.kbart.compare_coverage(Kbart(data)) == -365

    def test_coverage_with_embargo_R(self):
        data = ('My Journal', '1111-2222', '1111-2222', '', '', '',
                '', '', '', 'http://www.example.com', '', '', 'R1Y',
                '', '', '', 'My Publisher', 'journal')
        assert Kbart(data).coverage_length.days == 365

    def test_coverage_with_embargo_P(self):
        fake_coverage_begins = datetime.date.today() - datetime.timedelta(360)
        data = ('My Journal', '1111-2222', '1111-2222',
                fake_coverage_begins.strftime('%Y-%m-%d'), '', '',
                '', '', '', 'http://www.example.com', '', '', 'P6M',
                '', '', '', 'My Publisher', 'journal')
        assert Kbart(data).coverage_length.days == 180


if __name__ == '__main__':
    unittest.main()
