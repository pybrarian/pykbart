#!/usr/bin/env python
"""Read a csv of kbart records."""
# coding: utf-8
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import six
import unicodecsv as csv

import kbart.kbart


class Reader(six.Iterator):
    """"Class to read a file of KBART records."""

    def __init__(self,
                 file_handle,
                 provider=None,
                 rp=2,
                 delimiter='\t'):
        """Get csv.reader object from unicodecsv and get the header fields."""
        self.provider = provider
        self.rp = rp
        self.delimiter = delimiter
        self.reader = csv.reader(file_handle,
                                 delimiter=self.delimiter,
                                 encoding='utf-8')
        self.fields_from_header = [x for x in six.next(self.reader)]

    def __next__(self):
        """Return a Kbart instance from each csv line."""
        return kbart.kbart.Kbart(six.next(self.reader),
                                 provider=self.provider,
                                 rp=self.rp,
                                 fields=self.fields_from_header)

    def __iter__(self):
        return self

    def fields_pp(self):
        """Print a formatted representation of fields. Useful for debugging."""
        return ', '.join(map(str, self.fields_from_header))

    @property
    def fields(self):
        """Return field names of current kbart file."""
        return self.fields_from_header


class KbartReader():
    """Context manager for Reader classes."""

    def __init__(self,
                 file_name,
                 provider=None,
                 rp=2,
                 delimiter='\t'):
        """Only set variables to be used on entrance."""
        self.file_name = file_name
        self.provider = provider
        self.rp = rp
        self.delimiter = delimiter

    def __enter__(self):
        """Open all in binary mode when using unicodecsv."""
        self.f = open(self.file_name, 'rb')
        return Reader(self.f,
                      provider=self.provider,
                      rp=self.rp,
                      delimiter=self.delimiter)

    def __exit__(self, type, value, traceback):
        """Close file when leaving with scope."""
        self.f.close()
