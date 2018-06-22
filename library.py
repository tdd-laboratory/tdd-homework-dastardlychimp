import re
from typing import Tuple

_whole_word = lambda x: re.compile(r'(?<=\W)' + x + '(?=\W)')

_date_iso8601_pat = _whole_word(r'\d{4}-\d{2}-\d{2}')
_mixed_ordinal_pat = _whole_word(r'-?\d+(st|th|nd|rd)')
_integer_pat = _whole_word(r'\d+')
_floating_point_after_pat = re.compile(r'\.\d+[^a-zA-Z.]')
_floating_point_before_pat = re.compile(r'(?<=\d\.)')


DateTuple = Tuple[int, int, int]

def valid_date(date_tuple: DateTuple):
    '''Verify that the (year, month, day) DateTuple is a valid date.'''

    # Python way is to not check type, but otherwise floats would be valid.
    for v in date_tuple:
        if not isinstance(v, int):
            raise ValueError

    (year, month, day) = date_tuple
    valid = False

    if year > 0 and month > 0 and day > 0 and month < 13:
        if month == 2:
            if day == 29 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                valid = True
            elif day < 29:
                valid = True
        elif month in [4, 6, 9, 11] and day < 31:
            valid = True
        elif month in [1, 3, 5, 7, 8, 10, 12] and day < 32:
            valid = True

    return valid

def dates_iso8601(text):
    '''Find iso8601 dates in text, e.g. "2140-01-25" '''
    filter_non_dates = lambda rgx: map(int, rgx.groups())
    tuples_matches = map(lambda: rgx, rgx.groups(), _date_iso8601_pat.finditer(text))

def mixed_ordinals(text):
    '''Find tokens that begin with a number, and then have an ending like 1st or 2nd.'''
    for match in _mixed_ordinal_pat.finditer(text):
        yield('ordinal', match)

def integers(text):
    '''Find integers in text. Don't count floating point numbers.'''
    for match in _integer_pat.finditer(text):
        # If the integer we're looking at is part of a floating-point number, skip it.
        if _floating_point_before_pat.match(text, match.start()) or \
                _floating_point_after_pat.match(text, match.end()):
            continue
        yield ('integer', match)

def scan(text, *extractors):
    '''
    Scan text using the specified extractors. Return all hits, where each hit is a
    tuple where the first item is a string describing the extracted number, and the
    second item is the regex match where the extracted text was found.
    '''
    for extractor in extractors:
        for item in extractor(text):
            yield item
