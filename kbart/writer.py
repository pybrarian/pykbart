#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import,
    division, print_function, unicode_literals)

import csv
from io import open

class KbartWriter():

    def __init__(self, file_handle, fieldnames, delimiter='\t'):

        self.file_handle = file_handle
        self.fieldnames = fieldnames
        self.delimiter = delimiter

        self.writer = csv.DictWriter(file_handle,
                                     fieldnames=self.fieldnames,
                                     delimiter=self.delimiter)

        self.writer.writeheader()

    def write(self, kbart_record):

        try:
            self.writer.writerow(kbart_record.kbart_as_ordered_dict)
        except AttributeError:
            self.writer.writerow(kbart_record)

class WriterManager():

    def __init__(self, file_path, fieldnames, open_for='w', delimiter='\t'):
        self.file_path = file_path
        self.fieldnames = fieldnames
        self.delimiter = delimiter
        self.open_for = open_for

    def __enter__(self):
        self.f = open(self.file_path, self.open_for, encoding='utf-8')

        return KbartWriter(self.f, self.fieldnames, self.delimiter)

    def __exit__(self, type, value, traceback):
        self.f.close()

