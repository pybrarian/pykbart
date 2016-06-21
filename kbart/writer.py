#!/usr/bin/env python
"""Class and context manager for writing Kbart class to csv file."""
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import unicodecsv as csv


class Writer():
    """Write a Kbart class to a csv file."""

    def __init__(self, file_handle, delimiter='\t'):
        """Set variables and open the csv writer using utf-8 encoding."""
        self.file_handle = file_handle
        self.delimiter = delimiter
        self.writer = csv.writer(file_handle,
                                 delimiter=self.delimiter,
                                 encoding='utf-8')

    def writerow(self, kbart_record):
        """Write csv row from a Kbart record."""
        self.writer.writerow(kbart_record._kbart_data.values())

    def write_header(self, kbart_record):
        """Write the header."""
        self.writer.writerow(kbart_record.fields)


class KbartWriter():
    """Context manager for Writer class."""

    def __init__(self, file_path, delimiter='\t'):
        """Just variables."""
        self.file_path = file_path
        self.delimiter = delimiter

    def __enter__(self):
        self.f = open(self.file_name, 'wb')
        return Writer(self.f, self.delimiter)

    def __exit__(self, type, value, traceback):
        self.f.close()
