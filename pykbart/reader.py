#!/usr/bin/env python
"""Read a csv of kbart records."""
# coding: utf-8
from __future__ import (absolute_import, division, print_function)
import contextlib

import six

from kbart.kbart import Kbart

import unicodecsv as csv


def kbart_reader(file_handle, delimiter='\t'):
    reader = csv.reader(file_handle, delimiter=delimiter, encoding='utf-8')
    field_names = list(six.next(reader))
    for row in reader:
        yield Kbart(row, fields=field_names)


@contextlib.contextmanager
def KbartReader(file_path, delimiter='\t'):
    f = open(file_path, 'rb')
    try:
        yield kbart_reader(f, delimiter=delimiter)
    finally:
        f.close()
