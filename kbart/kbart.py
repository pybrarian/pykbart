#!/usr/bin/env python
"""Represent a Kbart in Python."""

# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from collections import OrderedDict
import re

import six

from kbart.constants import RP1_FIELDS, RP2_FIELDS, PROVIDER_FIELDS
from kbart.exceptions import InvalidRP, ProviderNotFound, UnknownEmbargoFormat


@six.python_2_unicode_compatible
class Kbart:
    """Kbart representation without having to remember field positions."""

    def __init__(self,
                 data=None,
                 provider=None,
                 rp=2,
                 fields=None):
        """
        Take or figure out the field names and zip them with values.

        Expected use is reading from a csv, but can build up the fields
        based on input.

        Args:
            data: Values for kbart fields, usually from csv
            provider: String of a publisher/provider's name. Kbart recommended
                practice allows publishers to define their own special fields
                to be tacked at the end. Some providers fields are provided. If
                not, just attach them to or pass them as 'fields'
            rp: Int of Recommended Practice version. Most organizations should
                be using RP2, but some early adopters, i.e. OCLC, still use
                RP1.
            fields: Iterable of field names to be attached to data.
                Will usually be passed from KbartReader class.
        """
        if data:
            self.data = data
        else:
            self.data = []
        self.provider = provider
        self.rp = rp
        self.embargo_pattern = re.compile('(R|P)(\d+)(D|M|Y)', re.I)

        if fields:
            self.fields = fields
        else:
            self.fields = list(RP1_FIELDS)
            if int(rp) == 2:
                self.fields.extend(RP2_FIELDS)
            elif not int(rp) == 1:
                raise InvalidRP

            if provider is not None:
                try:
                    self.fields.extend(PROVIDER_FIELDS[provider])
                except KeyError:
                    raise ProviderNotFound

        self._kbart_data = OrderedDict(six.moves.zip_longest(self.fields,
                                                             self.data,
                                                             fillvalue=''))
        self._holdings = Holdings(self.get_fields(
            'num_first_vol_online',
            'num_first_issue_online',
            'date_first_issue_online',
            'num_last_vol_online',
            'num_last_issue_online',
            'date_last_issue_online')
        )

    def __getitem__(self, key):
        if key in self._kbart_data:
            return self._kbart_data[key]
        else:
            raise KeyError

    def __setitem__(self, key, value):
        if key in self._kbart_data:
            self._kbart_data[key] = value
        else:
            raise KeyError

    def __repr__(self):
        return ("{0}(data={1}, provider={2}, rp={3}, fields={4})\n"
                .format(self.__class__.__name__,
                        self.data,
                        self.provider,
                        self.rp,
                        self.fields))

    def __str__(self):
        output = [" -------\n"]
        output.extend([_format_strings(the_string=self._kbart_data[key],
                                       prefix="{0}: ".format(key),
                                       suffix="\n")
                      for key in self._kbart_data])
        return "".join(output)

    def __len__(self):
        return len(self._kbart_data)

    def get_fields(self, *args):
        """Get values for the listed keys."""
        if not args:
            return self._kbart_data.values()

        return [self._kbart_data[x] for x in args
                if x in self._kbart_data]

    @property
    def serial_holdings(self):
        """Get a list of the serial holdings information available."""
        return self.holdings.holdings

    def serial_holdings_pp(self):
        """Formatted representation of serial holdings that exist."""
        return self.holdings.pretty_print()

    @property
    def title(self):
        return self._kbart_data['publication_title']

    @title.setter
    def title(self, value):
        self._kbart_data['publication_title'] = value

    @property
    def embargo(self):
        """
        Get embargo period for a journal in useful chunks.

        Embargo examples: R1Y - Moving wall, 1 year ago to present
                          P1Y - Embargo, coverage up to 1 year ago

        Returns:
            list of the embargo elements [type (r or p),
                                          length (int),
                                          magnitude (Years, Months, or Days)]
        Raises:
            UnknownEmbargoFormat: If the embargo coding is not properly
                formatted and can't be parsed by the RegEx
        """
        if self._kbart_data['embargo_info']:
            try:
                embargo_parts = self.embargo_pattern.match(
                    self._kbart_data['embargo_info'])
                return [embargo_parts.group(x).lower() for x in range(1, 4)]
            except AttributeError:
                raise UnknownEmbargoFormat
        else:
            return None

    @embargo.setter
    def embargo(self, value):
        if self.embargo_pattern.match(value):
            self._kbart_data['embargo_info'] = value
        else:
            raise UnknownEmbargoFormat

    def embargo_pp(self):
        """Formatted representation of available embargo information."""
        embargo_dict = {'d': 'day(s)', 'm': 'month(s)', 'y': 'year(s)',
                        'r': 'From {} {} ago to present',
                        'p': 'Up to {} {} ago'}

        if not self._kbart_data['embargo_info']:
            return None

        base_string = embargo_dict[self.embargo[0]]
        length_of_embargo = self.embargo[1]
        magnitude_of_length = embargo_dict[self.embargo[2]]

        return base_string.format(length_of_embargo, magnitude_of_length)

    @property
    def print_id(self):
        return self._kbart_data['print_identifier']

    @print_id.setter
    def print_id(self, value):
        self._kbart_data['print_identifier'] = value

    @property
    def e_id(self):
        return self._kbart_data['online_identifier']

    @e_id.setter
    def e_id(self, value):
        self._kbart_data['online_identifier'] = value

    @property
    def publisher(self):
        return self._kbart_data['publisher_name']

    @publisher.setter
    def publisher(self, value):
        self._kbart_data['publisher_name'] = value


class Holdings:

    def __init__(self, holding_fields):
        self.holdings = holding_fields
        self.first = self.holdings[:3]
        self.last = self.holdings[3:]

    def pretty_print(self):
        """Formatted representation of serial holdings that exist."""
        if any(self.holdings):
            first_holding = self._holdings_period(self.first)
            last_holding = self._holdings_period(self.last)
            if not last_holding:
                last_holding = 'present'

            return '{0} - {1}'.format(first_holding, last_holding)
        else:
            return ''

    @staticmethod
    def _holdings_period(holdings):
        return '{vol}{issue}{date}'.format(
            vol=_format_strings(holdings[0], prefix='Vol: ', suffix=', '),
            issue=_format_strings(holdings[1], prefix='Issue: ', suffix=', '),
            date=_format_strings(holdings[2])
        )

class Embargo:
    pass


def _format_strings(the_string='', prefix='', suffix=''):
    if the_string:
        return '{0}{1}{2}'.format(prefix, the_string, suffix)
    else:
        return ''
