#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import,
    division, print_function, unicode_literals)

import csv

import six

import kbart.kbart

class Kbart_reader(six.Iterator):

    def __init__(self,
                 file_handle,
                 provider=None,
                 rp=2,
                 has_header=True,
                 get_fields_from_header=False):
        self.reader = csv.reader(file_handle, delimiter='\t')
        self.provider = provider
        self.rp = rp
        self.fields_from_header = []

        if get_fields_from_header:
            self.fields_from_header = [x for x in six.next(self.reader)]
        elif has_header:
            six.next(self.reader)

    def __next__(self):
        return kbart.kbart.Kbart(six.next(self.reader),
                                 provider=self.provider,
                                 rp=self.rp,
                                 fields_from_header=self.fields_from_header)

    def __iter__(self):
        return self

    def list_fields(self):
        if self.fields_from_header:
            return ', '.join(map(str, self.fields_from_header))
        else:
            kbart_object = kbart.kbart.Kbart(provider=self.provider, rp=self.rp)
            return kbart_object.list_fields()
