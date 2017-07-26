import datetime
import re

from pykbart.exceptions import UnknownEmbargoFormat, IncompleteDateInformation

embargo_regex = re.compile('(?P<type>[RP])(?P<length>\d+)(?P<unit>[DMY])')
TODAY = datetime.date.today()
DATE_FORMAT = '%Y-%m-%d'


def embargo_as_dict(embargo):
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


def embargo_as_date(embargo):
    """
    Parse an embargo code and produce a date.

    Can call generically for beginning and ending dates becuase only called
    for the correct embargo type. Shouldn't fail as long as it's only
    called for records that actually have an embargo.

    KBART standard defines Month as 30 days and Year as 365 days, even
    though those are rough approximations, so we use that for conversion

    Returns: a datetime object
    """
    unit, length = embargo['unit'], int(embargo['length'])
    if unit == 'M':
        length *= 30
    elif unit == 'Y':
        length *= 365
    return TODAY - datetime.timedelta(length)


def check_embargo(embargo):
    if not re.match(embargo_regex, embargo):
        raise UnknownEmbargoFormat


# TODO: make able to compensate or warn for wrongly formatted dates
def parse_date_string(date):
    """
    Parse the date string from the KBART and make a datetime object.

    Add 1s until we have year, month, and day; if KBART record holding field
    is missing a month or day, we assume the first of that period, hence 1s.

    Reliant on dates being in KBART specified format.

    Args:
        date: the date string from a KBART date field

    Returns:
        a datetime object representing that date
    """
    date_parts = [int(x) for x in date.split('-')]
    while len(date_parts) < 3:
        date_parts.append(1)
    return datetime.date(*date_parts)


def coverage_begins(holdings, embargo):
    """
    Calculate and return the first date of coverage.

    Checks for embargo information first, then goes to the listed date. If
    embargo is an R, then coverage is the amount of the embargo back from
    today up to today.

    Returns: a datetime object for the last date of coverage

    Raises: IncompleteDateInformation: If no start date can be found or
        calculated.
    """
    if holdings[0]:
        begins = parse_date_string(holdings[0])
    elif embargo.get('type') == 'R':
        begins = embargo_as_date(embargo)
    else:
        raise IncompleteDateInformation
    return begins


def coverage_ends(holdings, embargo):
    """
    Calculate and return the last date of coverage.

    If embargo is an R, then coverage ends on current day (current issue
    release technically, but with embargoes there is no way to know). If
    embargo is P then the last coverage date is the amount of the embargo
    back from today. If no end-date or embargo information is there, KBART
    assumes coverage is to present.

    Returns: a datetime object for the last date of coverage
    """
    if holdings[3]:
        ends = parse_date_string(holdings[3])
    elif embargo.get('type') == 'P':
        ends = embargo_as_date(embargo)
    else:
        ends = TODAY
    return ends


def coverage_ends_text(holdings, embargo, date_format=DATE_FORMAT):
    ending_date = coverage_ends(holdings, embargo)
    if holdings[3]:
        return holdings[3]
    elif ending_date == TODAY:
        return 'Present'
    else:
        return ending_date.strftime(date_format)


def coverage_begins_text(holdings, embargo, date_format=DATE_FORMAT):
    return (holdings[0] if holdings[0]
            else coverage_begins(holdings, embargo).strftime(date_format))


def coverage_pretty_print(holdings, embargo, date_format=DATE_FORMAT):
    begin_vol, begin_issue = holdings[1], holdings[2]
    end_vol, end_issue = holdings[4], holdings[5]
    return '{0}{1}{2} - {3}{4}{5}'.format(
        coverage_begins_text(holdings, embargo, date_format),
        _volume_pp(begin_vol),
        _issue_pp(begin_issue),
        coverage_ends_text(holdings, embargo, date_format),
        _volume_pp(end_vol),
        _issue_pp(end_issue)
    )


def _volume_pp(vol):
    return ', Vol: ' + vol if vol else ''


def _issue_pp(issue):
    return ', Issue: ' + issue if issue else ''





