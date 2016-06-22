#!/usr/bin/env python


class ProviderNotFound(KeyError):
    def __str__(self):
        return ('That provider is not found. See documentation for supported'
                'providers.\n')


class InvalidRP(Exception):
    def __str__(self):
        return ('You entered an invalid Recommended Practice number. '
                'Please enter 1 or 2 (without quotes).\n')


class UnknownEmbargoFormat(Exception):
    def __str__(self):
        return ('Embargo code not recognized. '
                'Embargo should be formatted as R1Y or P1Y\n')


class IncompleteDateInformation(Exception):
    def __str__(self):
        return 'Insufficient date information to calculate coverage length.'
