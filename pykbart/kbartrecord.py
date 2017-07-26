#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from collections import OrderedDict, MutableMapping

import six

from pykbart.holdings import (coverage_begins, coverage_begins_text,
                              coverage_ends, coverage_ends_text, embargo_as_dict,
                              coverage_pretty_print, check_embargo)
from pykbart.constants import RP1_FIELDS, RP2_FIELDS, PROVIDER_FIELDS
from pykbart.exceptions import InvalidRP, ProviderNotFound


@six.python_2_unicode_compatible
class KbartRecord(MutableMapping):
    """KbartRecord representation without having to remember field positions."""

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
            provider: String of a publisher/provider's name. KbartRecord recommended
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
        return ('{0}(data={1}, provider={2}, rp={3}, fields={4})'
                .format(self.__class__.__name__,
                        six.moves.reprlib.repr([str(x) for x in self.data]),
                        str(self.provider),
                        self.rp,
                        six.moves.reprlib.repr(self.fields)))

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
        return iter(self._kbart_data)

    def get_fields(self, *args):
        """Get values for the listed keys."""
        if not args:
            return list(self._kbart_data.values())

        return [self._kbart_data[x] for x in args
                if x in self._kbart_data]

    @property
    def coverage_length(self):
        embargo, holdings = embargo_as_dict(self.embargo), self.holdings_fields
        return (coverage_ends(holdings, embargo) -
                coverage_begins(holdings, embargo))

    def compare_coverage(self, other_kbart):
        """
        Compare the coverage dates for this kbart instance against another.

        Args:
            other_kbart: Another KBART instance

        Returns: An int describing the coverage; positive means the current
            holding has better coverage by that many days, negative means the
            other KBART has better coverage, 0 is equal.

        """
        return self.coverage_length.days - other_kbart.coverage_length.days

    @property
    def start_date(self):
        embargo = embargo_as_dict(self.embargo)
        return coverage_begins_text(self.holdings_fields, embargo)

    @start_date.setter
    def start_date(self, value):
        self._kbart_data['date_first_issue_online'] = value

    @property
    def end_date(self):
        embargo = embargo_as_dict(self.embargo)
        return coverage_ends_text(self.holdings_fields, embargo)

    @end_date.setter
    def end_date(self, value):
        self._kbart_data['date_last_issue_online'] = value

    @property
    def coverage(self):
        embargo = embargo_as_dict(self.embargo)
        return coverage_pretty_print(self.holdings_fields, embargo)

    @property
    def embargo(self):
        return self._kbart_data['embargo_info']

    @embargo.setter
    def embargo(self, value):
        check_embargo(value)
        self._kbart_data['embargo_info'] = value

    @property
    def title(self):
        return self._kbart_data['publication_title']

    @title.setter
    def title(self, value):
        self._kbart_data['publication_title'] = value

    @property
    def url(self):
        return self._kbart_data['title_url']

    @url.setter
    def url(self, value):
        self._kbart_data['title_url'] = value

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

    @property
    def holdings_fields(self):
        return list(self._kbart_data.values())[3:9]


def _format_strings(the_string='', prefix='', suffix=''):
    """Small convenience function, allows easier logic in .format() calls"""
    if the_string:
        return '{0}{1}{2}'.format(prefix, the_string, suffix)
    else:
        return ''
