#!/usr/bin/env python

"""
USPS Form:  http://zip4.usps.com/zip4/citytown.jsp

Python script to fill out the USPS ZIP Code look-up form by city and
state.
"""

import os
import re
import csv
from urllib2 import urlopen
from mechanize import ParseResponse


def usps_form():
    """Return the USPS ZIP Code look-up form."""
    url = "http://zip4.usps.com/zip4/citytown.jsp"
    forms = ParseResponse(urlopen(url))
    form = forms[0]
    return form


def fill_out_form(form, **kwargs):
    """
    Given a form and keyword arguments -- fill out the form fields and
    return the resulting web page.
    """
    for key, value in kwargs.items():
        form[key] = value
    return urlopen(form.click()).read()


class ZipCodeScraper(object):
    """
    Scrape the USPS ZIP Code look-up site -- and optionally pass in the
    name of CSV file containing city and state values or a list of
    dictionaries containing city and state keys.
    """

    def __init__(self, csv_file=None):
        if csv_file:
            if isinstance(csv_file, str):
                self.cities = self.city_state_list(csv_file)
            elif isinstance(csv_file, list):
                self.cities = csv_file
        else:
            self.cities = None

    def city_state_list(self, csv_file):
        """
        Create a list of dictionaries from a CSV file of city and state
        values.
        """
        with open(csv_file) as f:
            reader = csv.reader(f)
            return [dict(city=row[0], state=row[1]) for row in reader]

    def save_html(self, directory='html'):
        """
        Get the HTML pages returned by a ZIP Code look-up and save them to
        a directory. The default directory for saving the HTML pages is `html`.
        """
        cities = self.cities
        form = usps_form()
        if not os.path.exists(directory):
            os.mkdir(directory)
        for index, city in enumerate(cities):
            html_data = fill_out_form(form, **city)
            city_name = re.sub(' ', '_', city['city'].lower())
            str_index = str(index).zfill(2)
            file_name = ''.join((str_index, '_', city_name, '.html'))
            self.write_to_directory(directory, file_name, html_data)

    def write_to_directory(self, directory, file_name, data):
        """Write a file in the given directory."""
        file_name = os.path.join(directory, file_name)
        with open(file_name, 'w') as f:
            f.write(data)


def main():
    # Uncomment the following to scrape the USPS site...
    # scraper = ZipCodeScraper('city_state.csv')
    # scraper.save_html()


if __name__ == '__main__':
    main()
