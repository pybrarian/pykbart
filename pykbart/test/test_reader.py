#!/usr/bin/env python
# coding: utf-8

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os.path
import unittest

from pykbart.reader import KbartReader


class TestKbartReader(unittest.TestCase):

    def test_general_runthrough(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        num_of_records = 0
        with KbartReader(os.path.join(directory, 'printHoldings.txt')) as reader:
            for record in reader:
                num_of_records += 1
        self.assertEqual(num_of_records, 965)


if __name__ == '__main__':
    unittest.main()
