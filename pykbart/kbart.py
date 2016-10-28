#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from collections import OrderedDict, MutableMapping
import datetime
import re

import six

from pykbart.constants import (RP1_FIELDS, RP2_FIELDS, PROVIDER_FIELDS,
                             EMBARGO_CODES_TO_STRINGS)
from pykbart.exceptions import (InvalidRP, ProviderNotFound,
                              UnknownEmbargoFormat, IncompleteDateInformation)


@six.python_2_unicode_compatible
class Kbart(MutableMapping):
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

    def __getitem__(self, key):
        """Delegate most work to the OrderedDict held by class."""
        return self._kbart_data[key]

    def __setitem__(self, key, value):
        self._kbart_data[key] = value

    def __delitem__(self, key):
        del(self._kbart_data[key])

    def __repr__(self):
        return ('{0}(data={1}, provider={2}, rp={3}, fields={4})\n'
                .format(self.__class__.__name__,
                        self.data,
                        self.provider,
                        self.rp,
                        self.fields))

    def __str__(self):
        output = [' -------\n']
        output.extend([_format_strings(the_string=self._kbart_data[key],
                                       prefix='{0}: '.format(key),
                                       suffix='\n')
                      for key in self._kbart_data])
        return ''.join(output)

    def __len__(self):
        return len(self._kbart_data)

    def __iter__(self):
        return self._kbart_data.__iter__()

    def get_fields(self, *args):
        """Get values for the listed keys."""
        if not args:
            return list(self._kbart_data.values())

        return [self._kbart_data[x] for x in args
                if x in self._kbart_data]

    @property
    def holdings(self):
        return list(self._kbart_data.values())[3:9]

    def holdings_pp(self):
        return Holdings.pretty_print(self.holdings)

    @property
    def title(self):
        return self._kbart_data['publication_title']

    @title.setter
    def title(self, value):
        self._kbart_data['publication_title'] = value

    @property
    def embargo(self):
        return self._kbart_data['embargo_info']

    @embargo.setter
    def embargo(self, value):
        if Embargo.check_embargo_format(value):
            self._kbart_data['embargo_info'] = value
        else:
            raise UnknownEmbargoFormat

    def embargo_pp(self):
        return Embargo.pretty_print(self.embargo)

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


class Holdings(object):
    """
    Essentially just a namespace class for holdings logic so the class meant
    to represent a KBART record doesn't also need to know how to think about
    holdings data and can delegate instead.
    """
    @staticmethod
    def pretty_print(holdings):
        """
        Make holdings information more readable to a human.

        Args:
            holdings: Iterable of the 6 KBART holdings fields.
                Slice [:3] are the first holding year, vol, issue
                Slice [3:] are the last year, vol, issue

        Returns:
            String representing the holdings or a message that no holdings
            exist.
        """
        if any(holdings):
            first_holding = Holdings._create_holdings_string(holdings[:3])
            last_holding = Holdings._create_holdings_string(holdings[3:])
            if not last_holding:  # KBART logic, no last holding = to present
                last_holding = 'present'
            return '{0} - {1}'.format(first_holding, last_holding)
        else:
            return 'No holdings present'

    @staticmethod
    def length_of_coverage(holdings):
        """
        If we have 2 dates, use them to determine length. Else assume holdings
        are 'to present', formulate a date and use that. If that doesn't work
        throw an exception that should be caught within the program.

        Returns:
            An int expressing how many years of coverage for that title

        Exceptions:
            IncompleteDateInformation: if no range can be produced
        """
        first_year, last_year = holdings[0], holdings[3]
        try:
            coverage_length = int(last_year) - int(first_year)
        except ValueError:
            try:
                this_year = datetime.datetime.now().year
                coverage_length = int(this_year) - int(first_year)
            except ValueError:
                raise IncompleteDateInformation

        return coverage_length

    @staticmethod
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
        return ', '.join(x for x in holdings if x)


class Embargo(object):
    """
    Essentially just a namespace class for embargo logic so the class meant
    to represent a KBART record doesn't also need to know how to think about
    embargo data and regexes etc. and can delegate instead.
    """

    # using named groups, so ?P<type> etc. are group names rather than
    # matching logic
    pattern = re.compile('(?P<type>R|P)(?P<length>\d+)(?P<unit>D|M|Y)')

    @staticmethod
    def pretty_print(embargo):
        """
        Change an embargo code, i.e. R1Y, to a human-readable string, i.e.
        'Up to 1 year ago'.

        Args:
            embargo: A KBART embargo string, i.e. R1Y
        Returns:
            A string stating the embargo information.
            KeyError is thrown if no embargo is passed and _embargo_as_dict
            returns a blank object, and in that case return empty string.
        """
        embargo_parts = Embargo._embargo_as_dict(embargo)
        try:
            type_of_embargo = EMBARGO_CODES_TO_STRINGS[embargo_parts['type']]
            units = EMBARGO_CODES_TO_STRINGS[embargo_parts['unit']]
            return type_of_embargo.format(embargo_parts['length'], units)
        except KeyError:
            return ''

    @staticmethod
    def _embargo_as_dict(embargo):
        """
        Take an embargo, break it up with the class level regex, and make
        it into a regular dict
        Args:
            embargo: A KBART embargo string, i.e. R1Y

        Returns:
            A dict containing the embargo sections, or an empty dict if no
            embargo. Empty dict is essentially Null Object pattern to avoid
            continuous error handling or existence checks when reading a
            KBART file.

        Raises:
            UnknownEmbargoFormat: If an embargo is passed but can't be parsed
        """
        if embargo:
            try:
                embargo_parts = Embargo.pattern.match(embargo)
                embargo_dict = embargo_parts.groupdict()
            except AttributeError:
                raise UnknownEmbargoFormat
        else:
            embargo_dict = {}
        return embargo_dict

    @staticmethod
    def check_embargo_format(embargo):
        return bool(Embargo.pattern.match(embargo))

def _format_strings(the_string='', prefix='', suffix=''):
    """Small convenience function, allows easier logic in .format() calls"""
    if the_string:
        return '{0}{1}{2}'.format(prefix, the_string, suffix)
    else:
        return ''
