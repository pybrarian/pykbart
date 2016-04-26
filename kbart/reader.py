#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import,
    division, print_function, unicode_literals)

import csv
from io import open

import six

import kbart.kbart

class Reader(six.Iterator):

    def __init__(self,
                 file_handle,
                 provider=None,
                 rp=2,
                 file_delimiter='\t'):

        self.reader = csv.reader(file_handle, delimiter=file_delimiter)
        self.provider = provider
        self.rp = rp

        self.fields_from_header = [x for x in six.next(self.reader)]


    def __next__(self):
        return kbart.kbart.Kbart(six.next(self.reader),
                                 provider=self.provider,
                                 rp=self.rp,
                                 fields_from_header=self.fields_from_header)

    def __iter__(self):
        return self

    def fields_pp(self):
        if self.fields_from_header:
            return ', '.join(map(str, self.fields_from_header))
        else:
            kbart_object = kbart.kbart.Kbart(provider=self.provider, rp=self.rp)
            return kbart_object.list_fields()

    @property
    def fields(self):
        if self.fields_from_header:
            return self.fields_from_header
        else:
            kbart_object = kbart.kbart.Kbart(provider=self.provider, rp=self.rp)
            return kbart_object.kbart_fields



class KbartReader():

    def __init__(self,
                 file_name,
                 provider=None,
                 rp=2,
                 file_delimiter='\t'):
        self.file_name = file_name
        self.provider=provider
        self.rp = rp
        self.file_delimiter = file_delimiter

    def __enter__(self):
        self.f = open(self.file_name, 'r', encoding='utf-8')
        return Reader(self.f,
                      provider=self.provider,
                      rp=self.rp,
                      file_delimiter=self.file_delimiter)

    def __exit__(self, type, value, traceback):
        self.f.close()
