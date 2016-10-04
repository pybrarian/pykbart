#!/usr/bin/env python
"""
This code represents and allows for manipulating a KBART file (the format
that controls all of our electronic holdings) programmatically. I have employed
this to do a variety of tasks, including but limited to checking our holdings
against vendor lists, taking count of our holdings, batch-updating local
collections, and routinely making backup copies of local collections.
This has made all of these tasks considerably more efficient than they
might otherwise be.
"""

# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


from collections import OrderedDict
import datetime
import re

import six

from kbart.constants import (RP1_FIELDS, RP2_FIELDS, PROVIDER_FIELDS,
                             EMBARGO_CODES_TO_STRINGS)
from kbart.exceptions import (InvalidRP, ProviderNotFound,
                              UnknownEmbargoFormat, IncompleteDateInformation)


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
        self.provider = provider
        self.rp = rp
        if data:
            self.data = data
        else:
            self.data = []

        if fields:
            self.fields = fields
        else:
            self.fields = self._create_fields()

        self._kbart_data = OrderedDict(six.moves.zip_longest(self.fields,
                                                             self.data,
                                                             fillvalue=''))
        # Ugly, but necessary to use values rather than data  to ensure blank
        # fields rather than no fields if user is building up a KBART instance
        # rather than reading in data
        holding_fields = self._kbart_data.values()[3:9]
        self.holdings = Holdings(holding_fields)
        self.embargo = Embargo(self._kbart_data['embargo_info'])

    def __getitem__(self, key):
        return self._kbart_data[key]

    def __setitem__(self, key, value):
        self._kbart_data[key] = value

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
        return self.holdings.holdings

    def serial_holdings_pp(self):
        return self.holdings.pretty_print()

    @property
    def title(self):
        return self._kbart_data['publication_title']

    @title.setter
    def title(self, value):
        self._kbart_data['publication_title'] = value

    def embargo_pp(self):
        return self.embargo.pretty_print()

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

    def _create_fields(self):
        fields = list(RP1_FIELDS)
        if int(self.rp) == 2:
            fields.extend(RP2_FIELDS)
        elif not int(self.rp) == 1:
            raise InvalidRP

        if self.provider is not None:
            try:
                fields.extend(PROVIDER_FIELDS[self.provider])
            except KeyError:
                raise ProviderNotFound

        return fields


class Holdings:

    def __init__(self, holding_fields):
        """
        Args:
            holding_fields: the slice of the KBART that has holdings info.
        [first_date, first_vol, first_issue, last_date, last_vol, last_issue]
        """
        self.holdings = holding_fields
        self.first_holding = self.holdings[:3]
        self.last_holding = self.holdings[3:]

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.holdings)

    def pretty_print(self):
        if any(self.holdings):
            first_holding = _create_holdings_string(self.first_holding)
            last_holding = _create_holdings_string(self.last_holding)

            if not last_holding:
                last_holding = 'present'

            return '{0} - {1}'.format(first_holding, last_holding)
        else:
            return 'No holdings present'

    @property
    def length_of_coverage(self):
        """
        If we have 2 dates, use them to determine length. Else assume holdings
        are 'to present', formulate a date and use that. If that doesn't work
        throw an exception that should be caught within the program.

        Returns:
            An int expressing how many years of coverage for that title

        Exceptions:
            IncompleteDateInformation: if no range can be produced
        """
        try:
            coverage_length = int(self.holdings[3]) - int(self.holdings[0])
        except ValueError:
            try:
                this_year = datetime.datetime.now().year
                coverage_length = int(this_year) - int(self.holdings[0])
            except ValueError:
                raise IncompleteDateInformation

        return coverage_length


class Embargo:

    def __init__(self, embargo):
        self.pattern = re.compile(
            '(?P<type>R|P)(?P<length>\d+)(?P<unit>D|M|Y)',
            re.I
        )
        self.embargo = embargo
        self.embargo_parts = self._embargo_as_dict()

    def __str__(self):
        return str(self.embargo)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.embargo)

    def pretty_print(self):
        try:
            type_of_embargo = EMBARGO_CODES_TO_STRINGS[self.embargo_parts['type']]
            length = self.embargo_parts['length']
            units = EMBARGO_CODES_TO_STRINGS[self.embargo_parts['unit']]

            return type_of_embargo.format(length, units)
        except KeyError:
            return ''

    def _embargo_as_dict(self):
        if self.embargo:
            try:
                embargo_parts = self.pattern.match(self.embargo)
                embargo_dict = embargo_parts.groupdict()
            except AttributeError:
                raise UnknownEmbargoFormat
        else:
            embargo_dict = {}

        return embargo_dict


def _create_holdings_string(holdings):
    """
    Format a section of KBART holdings into a human-readable string.
    Args:
        holdings: 3 element list; [date, vol, issue] following KBART order

    Returns:
        Human readable string of the holding period

    """
    holdings[1] = _format_strings(holdings[1], prefix='Vol: ')
    holdings[2] = _format_strings(holdings[2], prefix='Issue: ')
    return ', '.join([x for x in holdings if x])


def _format_strings(the_string='', prefix='', suffix=''):
    if the_string:
        return '{0}{1}{2}'.format(prefix, the_string, suffix)
    else:
        return ''
