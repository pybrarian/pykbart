#!/usr/bin/env python
"""Read a csv of kbart records."""
# coding: utf-8
from __future__ import (absolute_import, division, print_function)
import contextlib

import six

from pykbart.kbartrecord import KbartRecord

import unicodecsv as csv


class Reader(six.Iterator):

    def __init__(self, file_handle, delimiter='\t'):
        self.reader = csv.reader(file_handle, delimiter=delimiter, encoding='utf-8')
        self.fields = list(six.next(self.reader))

    def __next__(self):
        return KbartRecord(six.next(self.reader), fields=self.fields)

    def __iter__(self):
        return self


@contextlib.contextmanager
def KbartReader(file_path, delimiter='\t'):
    f = open(file_path, 'rb')
    try:
        yield Reader(f, delimiter=delimiter)
    finally:
        f.close()
