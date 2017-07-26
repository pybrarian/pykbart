#!/usr/bin/env python
"""Class and context manager for writing KbartRecord class to csv file."""
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import contextlib

import six
import unicodecsv as csv


# TODO: make a better way to write the header when working from a reader object
class Writer(object):
    """Write a KbartRecord class to a csv file."""

    def __init__(self, file_handle, delimiter='\t'):
        """
        Set variables and open the csv writer using utf-8 encoding per
        KBART spec.
        """
        self.file_handle = file_handle
        self.delimiter = delimiter
        self.writer = csv.writer(file_handle,
                                 delimiter=self.delimiter,
                                 encoding='utf-8')

    def writerow(self, kbart_record):
        """Write csv row from a KbartRecord record."""
        self.writer.writerow(list(kbart_record.values()))

    def writeheader(self, kbart_record):
        self.writer.writerow(kbart_record.fields)


@contextlib.contextmanager
def KbartWriter(file_path, delimiter='\t'):
    """
    Context manager for writing a KbartRecord. Written in camel-case to maintain
    similarity to PyMARC.

    Args:
        file_path: The path to the KBART file to be written.
        delimiter: KBART spec specifies tab-delimited, leaving this an option
            though for the time being
    """
    f = open(file_path, 'wb')
    try:
        yield Writer(f, delimiter=delimiter)
    finally:
        f.close()
