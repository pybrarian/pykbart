#!/usr/bin/env python
"""Read a csv of kbart records."""
# coding: utf-8
from __future__ import (absolute_import, division, print_function)
import contextlib

import six

from kbart.kbart import Kbart

if six.PY2:
    import unicodecsv as csv
else:
    import csv


def kbart_reader(file_handle, provider=None, rp=2, delimiter='\t'):
    reader = csv.reader(file_handle, delimiter=delimiter, encoding='utf-8')
    field_names = list(six.next(reader))
    for row in reader:
        yield Kbart(row, provider=provider, rp=rp, fields=field_names)


@contextlib.contextmanager
def KbartReader(file_path, provider=None, rp=2, delimiter='\t'):
    f = open(file_path, 'rb')
    try:
        yield kbart_reader(f, provider=provider, rp=rp, delimiter=delimiter)
    finally:
        f.close()
