import unittest
import library

NUM_CORPUS = '''
On the 5th of May every year, Mexicans celebrate Cinco de Mayo. This tradition
began in 1845 (the twenty-second anniversary of the Mexican Revolution), and
is the 1st example of a national independence holiday becoming popular in the
Western Hemisphere. (The Fourth of July didn't see regular celebration in the
US until 15-20 years later.) It is celebrated by 77.9% of the population--
trending toward 80.                                                                
'''

class TestCase(unittest.TestCase):

    # Helper function
    def assert_extract(self, text, extractors, *expected):
        actual = [x[1].group(0) for x in library.scan(text, extractors)]
        self.assertEqual(str(actual), str([x for x in expected]))

    # First unit test; prove that if we scan NUM_CORPUS looking for mixed_ordinals,
    # we find "5th" and "1st".
    def test_mixed_ordinals(self):
        self.assert_extract(NUM_CORPUS, library.mixed_ordinals, '5th', '1st')

    # Second unit test; prove that if we look for integers, we find four of them.
    def test_integers(self):
        self.assert_extract(NUM_CORPUS, library.integers, '1845', '15', '20', '80')

    def test_integers_comma_sepearated(self):
        self.assert_extract('This is a , separated number list: 12,3242,15', '12', '3242', '15')


    # Third unit test; prove that if we look for integers where there are none, we get no results.
    def test_no_integers(self):
        self.assert_extract("no integers", library.integers)

class TestExtractISO8601(unittest.TestCase):

    def assert_extract(self, text, *expected):
        actual = [x[1].group(0) for x in library.dates_iso8601(text)]
        self.assertEqual(actual, list(expected))

    def test_extract_string(self):
        self.assert_extract("I was born on 2015-07-25 .", "2015-07-25")
        self.assert_extract("I was born on 1842-01-03.", "1842-01-03")
        self.assert_extract("I was born on 5426-07-25.", "5426-07-25")

    def test_month_larger_than_12(self):
        self.assert_extract("I was born on 2015-13-25.")

    def test_month_less_than_1(self):
        self.assert_extract("I was born on 2015-00-25.")

    def test_date_greater_than_31(self):
        self.assert_extract("I was born on 2015-07-32.")

    def test_date_less_than_1(self):
        self.assert_extract("I was born on 2015-07-00.")

    def test_months_30(self):
        self.assert_extract("I was born on 2015-04-31.")
        self.assert_extract("I was born on 2015-06-31.")
        self.assert_extract("I was born on 2015-09-31.")
        self.assert_extract("I was born on 2015-11-31.")
        self.assert_extract("I was born on 2010-04-30.", "2010-04-30")

    def test_months_31(self):
        self.assert_extract("I was born on 2015-01-31.", "2015-01-31")
        self.assert_extract("I was born on 2015-03-31.", "2015-03-31")
        self.assert_extract("I was born on 2015-05-31.", "2015-05-31")
        self.assert_extract("I was born on 2015-07-31.", "2015-07-31")
        self.assert_extract("I was born on 2015-08-31.", "2015-08-31")
        self.assert_extract("I was born on 2015-10-31.", "2015-10-31")
        self.assert_extract("I was born on 2015-12-31.", "2015-12-31")

    def test_february_28(self):
        self.assert_extract("I was born on 2015-02-29.")

    def test_february_29(self):
        self.assert_extract("I was born on 2000-02-29.", "2000-02-29")

    def test_no_dash_years(self):
        self.assert_extract("I was born on -294-01-01.")

    def test_invalid_seperator(self):
        self.assert_extract("I was born on 1845:04:10.")

    def test_end_beginning_of_line(self):
        self.assert_extract("I was born on 2015-07-25", "2015-07-25")
        self.assert_extract("2015-07-25, was I was born on.", "2015-07-25")

    def test_multiple_addresses(self):
        self.assert_extract("I was born on 2015-07-25, not on 2015-07-26.", "2015-07-25", "2015-07-26")
        self.assert_extract("I was not born on 2015-13-02 because it is invalid, but on 2000-12-01", "2000-12-01")

    def test_timestamp_hours(self):
        self.assert_extract("I was born on 2015-07-25 23", "2015-07-25 23")
        self.assert_extract("I was born on 2015-07-25 00", "2015-07-25 00")
        self.assert_extract("I was born on 2015-07-25 2")
        self.assert_extract("I was born on 2015-07-25 25")

    def test_timestamp_minutes(self):
        self.assert_extract("I was born on 2015-07-25 23:14", "2015-07-25 23:14")
        self.assert_extract("I was born on 2015-07-25 00:00", "2015-07-25 00:00")
        self.assert_extract("I was born on 2015-07-25 23:1")
        self.assert_extract("I was born on 2015-07-25 11:61")

    def test_timestamp_seconds(self):
        self.assert_extract("I was born on 2015-07-25 23:14:12", "2015-07-25 23:14:12")
        self.assert_extract("I was born on 2015-07-25 11:11:00", "2015-07-25 11:11:00")
        self.assert_extract("I was born on 2015-07-25 23:14:1")
        self.assert_extract("I was born on 2015-07-25 04:12:61")
    
    def test_timestamp_milliseconds(self):
        self.assert_extract("I was born on 2015-07-25 23:14:12.943", "2015-07-25 23:14:12.943")
        self.assert_extract("I was born on 2015-07-25 11:11:12:000", "2015-07-25 11:11:12:000")
        self.assert_extract("I was born on 2015-07-25 23:14:12.1")
        self.assert_extract("I was born on 2015-07-25 04:12:58:0721")
    

    def test_timestamp_timezones(self):
        self.assert_extract("I was born on 2015-07-25 23MDT", "2015-07-25 23MDT")
        self.assert_extract("I was born on 2015-07-25 23:14UTC", "2015-07-25 23:14UTC")
        self.assert_extract("I was born on 2015-07-25 23:14:12Z", "2015-07-25 23:14:12Z")
        self.assert_extract("I was born on 2015-07-25 23:14:12.943UTC", "2015-07-25 23:14:12.943UTC")
        self.assert_extract("I was born on 2015-07-25 23:14:12.943-0800", "2015-07-25 23:14:12.943-0800")
        self.assert_extract("I was born on 2015-07-25 23:14:12.943-0000", "2015-07-25 23:14:12.943-0000")
        self.assert_extract("I was born on 2015-07-25 23:14:12.943Z-0800")
        self.assert_extract("I was born on 2015-07-25 23:14:12.943-000")
        self.assert_extract("I was born on 2015-07-25 23MT")
        self.assert_extract("I was born on 2015-07-25MDT")

    def test_timestamp_multiple(self):
        text_multiple_dates = '''
            This is a large pice of text with several timezones:
                2015-07-25 23:14:12.943-0800
                2015-07-25 23:14:12
                2015-12-31.
            We even have a couple of invalid ones too
                2015-07-25 04:12:58:0721
                2015-09-31.
        '''
        self.assert_extract(text_multiple_dates, "2015-07-25 23:14:12.943-0800", "2015-07-25 23:14:12", "2015-12-31")

    def test_timestamp_delimiter(self):
        self.assert_extract("I was born on 2015-07-25T23MDT", "2015-07-25T23MDT")
        self.assert_extract("I was born on 2015-07-25T23:14UTC", "2015-07-25T23:14UTC")
        self.assert_extract("I was born on 2015-07-25T23:14:12Z", "2015-07-25T23:14:12Z")
        self.assert_extract("I was born on 2015-07-25T23:14:12.943UTC", "2015-07-25T23:14:12.943")
        self.assert_extract("I was born on 2015-07-25T23:14:12.943-0800", "2015-07-25T23:14:12.943-0800")
        self.assert_extract("I was born on 2015-07-25:23MDT")
        self.assert_extract("I was born on 2015-07-25-23MDT")

class TestValidDate(unittest.TestCase):

    def valid_date(self, date_tuple, successful):
        self.assertEqual(library.valid_date(date_tuple), successful)

    def test_date_invalid_param(self):
        self.assertRaises(ValueError, self.valid_date, "(1, 3, 3)", False)
        self.assertRaises(ValueError, self.valid_date, (12, 2), False)
        self.assertRaises(ValueError, self.valid_date, (2000, 3.14, 2), False)
        self.assertRaises(ValueError, self.valid_date, (2000, 3, "4"), False)

    def test_date_negtaive(self):
        self.valid_date((-100, 1, 1), False)
        self.valid_date((101, -11, 1), False)
        self.valid_date((219, 1, -4), False)

    def test_date_0(self):
        self.valid_date((0, 1, 1), False)
        self.valid_date((101, 0, 1), False)
        self.valid_date((219, 1, 0), False)

    def test_month_too_large(self):
        self.valid_date((2031, 13, 3), False)

    def test_months_30(self):
        self.valid_date((2000, 4, 31), False)
        self.valid_date((2000, 6, 31), False)
        self.valid_date((2000, 9, 31), False)
        self.valid_date((2000, 11, 31), False)
        self.valid_date((2000, 4, 30), True)
        self.valid_date((2000, 6, 30), True)
        self.valid_date((2000, 9, 30), True)
        self.valid_date((2000, 11, 30), True)

    def test_months_31(self):
        self.valid_date((2000, 1, 31), True)
        self.valid_date((2000, 3, 31), True)
        self.valid_date((2000, 5, 31), True)
        self.valid_date((2000, 7, 31), True)
        self.valid_date((2000, 8, 31), True)
        self.valid_date((2000, 10, 31), True)
        self.valid_date((2000, 12, 31), True)
        self.valid_date((2000, 1, 32), False)
        self.valid_date((2000, 3, 32), False)
        self.valid_date((2000, 5, 32), False)
        self.valid_date((2000, 7, 32), False)
        self.valid_date((2000, 8, 32), False)
        self.valid_date((2000, 10, 32), False)
        self.valid_date((2000, 12, 32), False)

    def test_month_february(self):
        self.valid_date((1600, 2, 29), True)
        self.valid_date((1700, 2, 29), False)
        self.valid_date((2004, 2, 29), True)
        self.valid_date((2003, 2, 29), False)
        self.valid_date((2003, 2, 28), True)
        self.valid_date((2000, 2, 29), True)
        
class TestExtractDateWordMonth(unittest.TestCase):
    def assert_extract(self, text, *expected):
        actual = [x[1].group(0) for x in library.dates_month_word(text)]
        self.assertEqual(actual, list(expected))

    def test_extract_string_every_month(self):
        self.assert_extract("I was born on 25 Jan 1911.", "25 Jan 1911")
        self.assert_extract("I was born on 25 Feb 2015.", "25 Feb 2015")
        self.assert_extract("I was born on 03 Mar 2015.", "03 Mar 2015")
        self.assert_extract("I was born on 25 Apr 9382.", "25 Apr 9382")
        self.assert_extract("I was born on 25 May 2015.", "25 May 2015")
        self.assert_extract("I was born on 11 Jun 2015.", "11 Jun 2015")
        self.assert_extract("I was born on 25 Jul 2015.", "25 Jul 2015")
        self.assert_extract("I was born on 25 Aug 2015.", "25 Aug 2015")
        self.assert_extract("I was born on 25 Sep 0012.", "25 Sep 0012")
        self.assert_extract("I was born on 25 Oct 2015.", "25 Oct 2015")
        self.assert_extract("I was born on 25 Nov 2413.", "25 Nov 2413")
        self.assert_extract("I was born on 25 Dec 2015.", "25 Dec 2015")

    def test_extract_string_with_comma(self):
        self.assert_extract("I was born on 25 Jan, 1911.", "25 Jan, 1911")
        self.assert_extract("I was born on 25 Feb, 2015.", "25 Feb, 2015")
        self.assert_extract("I was born on 03 Mar, 2015.", "03 Mar, 2015")
        self.assert_extract("I was born on 25 Apr, 9382.", "25 Apr, 9382")
        self.assert_extract("I was born on 25 May, 2015.", "25 May, 2015")
        self.assert_extract("I was born on 11 Jun, 2015.", "11 Jun, 2015")
        self.assert_extract("I was born on 25 Jul, 2015.", "25 Jul, 2015")
        self.assert_extract("I was born on 25 Aug, 2015.", "25 Aug, 2015")
        self.assert_extract("I was born on 25 Sep, 0012.", "25 Sep, 0012")
        self.assert_extract("I was born on 25 Oct, 2015.", "25 Oct, 2015")
        self.assert_extract("I was born on 25 Nov, 2413.", "25 Nov, 2413")
        self.assert_extract("I was born on 25 Dec, 2015.", "25 Dec, 2015")

    def test_invalid_month(self):
        self.assert_extract("I was born on 25 Gru 2015.")
        self.assert_extract("I was born on 25 March 2015.")
        self.assert_extract("I was born on 25 Ja 2015.")
        self.assert_extract("I was born on 25 jan 2015.")

    def test_day_greater_than_31(self):
        self.assert_extract("I was born on 32 Jan 2015.")

    def test_date_less_than_1(self):
        self.assert_extract("I was born on 00 Jul 2015.")

    def test_months_30(self):
        self.assert_extract("I was born on 31 Apr 2015.")
        self.assert_extract("I was born on 31 Jun 2015.")
        self.assert_extract("I was born on 31 Sep 2015.")
        self.assert_extract("I was born on 31 Nov 2015.")

    def test_months_31(self):
        self.assert_extract("I was born on 31 Jan 2015.", "31 Jan 2015")
        self.assert_extract("I was born on 31 Mar 2015.", "31 Mar 2015")
        self.assert_extract("I was born on 31 May 2015.", "31 May 2015")
        self.assert_extract("I was born on 31 Jul 2015.", "31 Jul 2015")
        self.assert_extract("I was born on 31 Aug 2015.", "31 Aug 2015")
        self.assert_extract("I was born on 31 Oct 2015.", "31 Oct 2015")
        self.assert_extract("I was born on 31 Dec 2015.", "31 Dec 2015")

    def test_month_february(self):
        self.assert_extract("I was born on 29 Feb 2015.")
        self.assert_extract("I was born on 29 Feb 2000.", "29 Feb 2000")

    def test_end_beginning_of_line(self):
        self.assert_extract("I was born on 25 Jul 2015", "25 Jul 2015")
        self.assert_extract("25 Jul 2015, was I was born on.", "25 Jul 2015")

    def test_multiple_addresses(self):
        self.assert_extract("I was born on 25 Jul 2015, not on 26 Jul 2015.", "25 Jul 2015", "26 Jul 2015")
        self.assert_extract("I was not born on Jan 32 2015 because it is invalid, but on 01 Jan 2015.", "01 Jan 2015")
 

if __name__ == '__main__':
    unittest.main()
