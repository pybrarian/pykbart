import datetime
import re

from pykbart.exceptions import UnknownEmbargoFormat, IncompleteDateInformation

embargo_regex = re.compile('(?P<type>[RP])(?P<length>\d+)(?P<unit>[DMY])')
TODAY = datetime.date.today()
DATE_FORMAT = '%Y-%m-%d'


class Holdings(object):

    def __init__(self, holding_dates, embargo):
        self.holding_dates = holding_dates
        self.embargo_code = embargo
        self.embargo = self._embargo_as_dict(embargo)
        self.begins = None
        self.ends = None

    def pretty_print(self, date_format=DATE_FORMAT):
        begin_vol, begin_issue = self.holding_dates[1], self.holding_dates[2]
        end_vol, end_issue = self.holding_dates[4], self.holding_dates[5]
        return '{0}{1}{2} - {3}{4}{5}'.format(
            self.begins(date_format),
            self._volume_pp(begin_vol),
            self._issue_pp(begin_issue),
            self.ends(date_format),
            self._volume_pp(end_vol),
            self._issue_pp(end_issue)
        )

    def _volume_pp(self, vol):
        return ', Vol: ' + vol if vol else ''

    def _issue_pp(self, issue):
        return ', Issue: ' + issue if issue else ''

    def begins(self, date_format):
        return (self.holding_dates[0] if self.holding_dates[0]
                else self.coverage_begins.strftime(date_format))

    def ends(self, date_format):
        if self.holding_dates[3]:
            return self.holding_dates[3]
        elif self.coverage_ends == TODAY:
            return 'Present'
        else:
            return self.coverage_ends.strftime(date_format)

    @property
    def coverage_length(self):
        return self.coverage_ends - self.coverage_begins

    @property
    def coverage_begins(self):
        """
        Calculate and return the first date of coverage.

        Checks for embargo information first, then goes to the listed date. If
        embargo is an R, then coverage is the amount of the embargo back from
        today up to today.

        Returns: a datetime object for the last date of coverage
        
        Raises: IncompleteDateInformation: If no start date can be found or
            calculated.
        """
        if self.begins:
            begins = self.begins
        elif self.holding_dates[0]:
            begins = self._parse_date_string(self.holding_dates[0])
        elif self.embargo.get('type') == 'R':
            begins = self._embargo_as_date()
        else:
            raise IncompleteDateInformation
        self.begins = begins
        return begins

    @property
    def coverage_ends(self):
        """
        Calculate and return the last date of coverage.
        
        If embargo is an R, then coverage ends on current day (current issue
        release technically, but with embargoes there is no way to know). If
        embargo is P then the last coverage date is the amount of the embargo
        back from today. If no end-date or embargo information is there, KBART
        assumes coverage is to present.
        
        Returns: a datetime object for the last date of coverage
        """
        if self.ends:
            ends = self.ends
        elif self.holding_dates[3]:
            ends = self._parse_date_string(self.holding_dates[3])
        elif self.embargo.get('type') == 'R':
            ends = TODAY
        elif self.embargo.get('type') == 'P':
            ends = self._embargo_as_date()
        else:
            ends = TODAY
        self.ends = ends
        return ends

    def _embargo_as_dict(self, embargo):
        """
        Take an embargo, break it up with the class level regex, and make
        it into a regular dict

        Returns:
            A dict containing the embargo sections, or an empty dict if no
            embargo. Empty dict is essentially Null Object pattern to avoid
            continuous error handling or existence checks when reading a
            KBART file.

        Raises:
            UnknownEmbargoFormat: If an embargo is passed but can't be parsed
        """
        if embargo:
            try:
                embargo_parts = embargo_regex.match(embargo)
                embargo_dict = embargo_parts.groupdict()
            except AttributeError:
                raise UnknownEmbargoFormat
        else:
            embargo_dict = {}
        return embargo_dict

    def _embargo_as_date(self):
        """
        Parse an embargo code and produce a date.
        
        Can call generically for beginning and ending dates becuase only called
        for the correct embargo type. Shouldn't fail as long as it's only
        called for records that actually have an embargo.
        
        KBART standard defines Month as 30 days and Year as 365 days, even
        though those are rough approximations, so we use that for conversion
        
        Returns: a datetime object
        """
        unit, length = self.embargo['unit'], int(self.embargo['length'])
        if unit == 'M':
            length *= 30
        elif unit == 'Y':
            length *= 365
        return TODAY - datetime.timedelta(length)

    def _parse_date_string(self, date):
        """
        Parse the date string from the KBART and make a datetime object.
        
        Add 1s until we have year, month, and day; in the absence of information
        take the most optimistic possibility.
        
        Args:
            date: the date string from a KBART date field

        Returns:
            a datetime object representing that date
        """
        date_parts = [int(x) for x in date.split('-')]
        while len(date_parts) < 3:
            date_parts.append(1)
        return datetime.date(*date_parts)
