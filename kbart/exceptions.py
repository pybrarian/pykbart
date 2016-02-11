#!/usr/bin/env python
class ProviderNotFound(KeyError):

    def __str__(self):
        return ('That provider is not found. See documentation for supported'
                'providers.\n')

class NotValidRP(Exception):

    def __str__(self):
        return ('You entered an invalid Recommended Practice number. '
                'Please enter 1 or 2 (without quotes).\n')

class KeyNotFound(KeyError):

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return ('"{}" is not a valid key. '
                'Use .fields_pp() to see valid keys.\n'.format(self.key))