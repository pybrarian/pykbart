#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import,
    division, print_function, unicode_literals)

from collections import OrderedDict
import re

import six

import kbart.exceptions

@six.python_2_unicode_compatible
class Kbart():

    def __init__(self,
                 data=[],
                 provider=None,
                 rp=2,
                 fields_from_header=[]):

        self.data = data
        self.provider = provider
        self.rp = rp
        self.fields_from_header = fields_from_header

        if fields_from_header:
            self.kbart_fields = fields_from_header
        else:
            self.kbart_fields = [
                'publication_title', 'print_identifier', 'online_identifier',
                'date_first_issue_online', 'num_first_vol_online',
                'num_first_issue_online', 'date_last_issue_online',
                'num_last_vol_online', 'num_last_issue_online', 'title_url',
                'first_author', 'title_id', 'embargo_info',  'coverage_depth',
                'coverage_notes'
            ]

            self.kbart_fields_two = [
                'notes', 'publisher_name', 'publication_type',
                'date_monograph_published_print',
                'date_monograph_published_online', 'monograph_volume',
                'monograph_edition', 'first_editor',
                'parent_publication_title_id', 'preceding_publication_title_id',
                'access_type'
            ]

            self.provider_fields = {
                'oclc': [
                    'publisher_name', 'location', 'title_notes',
                    'staff_notes', 'vendor_id', 'oclc_collection_name',
                    'oclc_collection_id', 'oclc_entry_id', 'oclc_linkscheme',
                    'oclc_number', 'ACTION'
                ],
                'gale': [
                    'series_title', 'series_number', 'description', 'audience',
                    'frequency', 'format', 'referred_peer_re-viewed', 'country',
                    'language', 'primary_subject'
                ]
            }

            if int(rp) == 2:
                self.kbart_fields.extend(self.kbart_fields_two)
            elif not int(rp) == 1:
                raise kbart.exceptions.NotValidRP

            if provider is None:
                pass
            elif provider in self.provider_fields:
                self.kbart_fields.extend(self.provider_fields[provider])
            else:
                raise kbart.exceptions.ProviderNotFound

        self.kbart_as_ordered_dict = OrderedDict(six.moves.zip_longest(
                                                     self.kbart_fields,
                                                     data,
                                                     fillvalue=''))

    def __getitem__(self, key):
        if key in self.kbart_as_ordered_dict:
            return self.kbart_as_ordered_dict[key]
        else:
            raise kbart.exceptions.KeyNotFound(key)

    def __setitem__(self, key, value):
        if key in self.kbart_as_ordered_dict:
            self.kbart_as_ordered_dict[key] = value
        else:
            raise kbart.exceptions.KeyNotFound(key)

    def __repr__(self):
        return ("{}(data={}, provider={}, rp={}, fields_from_header={})\n"
                .format(self.__class__.__name__,
                        self.data,
                        self.provider,
                        self.rp,
                        self.fields_from_header))

    def __str__(self):
        output = [" -------\n"]

        output.extend([self._format_strings(
                          the_string=self.kbart_as_ordered_dict[key],
                          prefix="{}: ".format(key),
                          suffix="\n")
                      for key in self.kbart_as_ordered_dict])

        return "".join(output)

    def __len__(self):
        return len(self.kbart_as_ordered_dict)

    def get_fields(self, *args):

        if not args:
            return self.kbart_as_ordered_dict

        return [self.kbart_as_ordered_dict[x] for x in args
                if x in self.kbart_as_ordered_dict]

    def fields_pp(self):
        return ', '.join(map(str, self.kbart_fields))

    def serial_holdings(self):
        return self.get_fields('date_first_issue_online',
                               'num_first_vol_online',
                               'num_first_issue_online',
                               'date_last_issue_online',
                               'num_last_vol_online',
                               'num_last_issue_online')

#    def coverage_length(self):



    def serial_holdings_pp(self):

        holding_fields = self.serial_holdings()

        if any(holding_fields):

            holdings = (
                '{vol1}{issue1}{date1} - {vol2}{issue2}{date2}{emb}'.format(
                    vol1=self._format_strings(holding_fields[1], prefix='Volume: '),
                    issue1=self._format_strings(holding_fields[2], prefix=', Issue: '),
                    date1=self._format_strings(holding_fields[0]),
                    vol2=self._format_strings(holding_fields[4], prefix='Volume: '),
                    issue2=self._format_strings(holding_fields[5], prefix=', Issue: '),
                    date2=self._format_strings(holding_fields[3]),
                    emb=self._format_strings(self.embargo_pp())
                )
            )
        else:
            holdings = self.embargo_pp()

        return holdings

    def embargo_pp(self):

        embargo_dict = {'d': 'day(s)', 'm': 'month(s)', 'y': 'year(s)',
                        'r': 'From {} {} ago to present',
                        'p': 'Up to {} {} ago'}

        if not self.kbart_as_ordered_dict['embargo_info']:
            return None

        return embargo_dict[self.embargo[0]].format(self.embargo[1],
                                      embargo_dict[self.embargo[2]])

    @property
    def title(self):
        return self.kbart_as_ordered_dict['publication_title']

    @title.setter
    def title(self, value):
        self.kbart_as_ordered_dict['publication_title'] = value

    @property
    def embargo(self):
        if self.kbart_as_ordered_dict['embargo_info']:
            embargo_parts = re.match('(R|P)(\d+)(D|M|Y)',
                                     self.kbart_as_ordered_dict['embargo_info'],
                                     flags=re.I)

            return [embargo_parts.group(x).lower() for x in range(1, 4)]
        else:
            return None

    def _format_strings(self, the_string='', prefix='', suffix='', decode=True):
        '''
        if decode:
            the_string = the_string.decode('utf-8')
        '''

        if the_string:
            return '{0}{1}{2}'.format(prefix, the_string, suffix)
        else:
            return ''
