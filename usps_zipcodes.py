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

import lxml.html as lh
from mechanize import ParseResponse


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

    def usps_form(self):
        """Return the USPS ZIP Code look-up form."""
        url = "http://zip4.usps.com/zip4/citytown.jsp"
        forms = ParseResponse(urlopen(url))
        form = forms[0]
        return form

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
        form = self.usps_form()
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


class ZipCodeParser(object):
    """
    Look through a directory of HTML pages scraped from the USPS website and
    parse the pages for actual ZIP Codes.
    """

    def __init__(self, directory=None, filter_results=True):
        self.directory = directory
        self.filter_results = filter_results

    def find_html_pages(self, directory='html'):
        """
        Find the HTML pages that are saved in a given directory -- by default
        that directory is `html`.
        """
        for root, dirs, files in os.walk(directory):
            return [os.path.join(root, f) for f in files
                    if f.endswith('.html')]

    def scrape_zip_codes(self, document):
        """Scrape a given USPS ZIP Code web page with the lxml.html module."""
        html = lh.fromstring(document)
        td_list = html.cssselect('td.main')
        zip_codes = (td.text.strip() for td in td_list)
        return self.filter_zip_codes(zip_codes)

    def filter_zip_codes(self, zip_codes):
        """
        This function filters the ZIP Codes -- I specifically am not looking for
        ZIP Codes with a long length, because those are only used for PO Boxes.
        """
        if not self.filter_results:
            return list(zip_codes)
        check_length = lambda text: len(text) < 15
        return filter(check_length, zip_codes)

    def parse_all(self, directory=None):
        """Parse all the HTML pages in a given directory for ZIP Codes."""
        if not directory:
            directory = self.directory
        all_zip_codes = []
        files = self.find_html_pages(directory)
        for file_name in files:
            with open(file_name) as f:
                document = f.read()
            zip_codes = self.scrape_zip_codes(document)
            all_zip_codes.extend(zip_codes)
        return all_zip_codes


def save_zip_codes(file_name, zip_codes):
    """Write the obtained ZIP Codes to a file."""
    with open(file_name, 'w') as f:
        # For some reason writelines writes out just a blob
        # of text rather than an individual line.
        for line in zip_codes:
            f.write(line)
            f.write('\n')


def main():
    # Uncomment the following to scrape the USPS site...
    # scraper = ZipCodeScraper('city_state.csv')
    # scraper.save_html()
    parser = ZipCodeParser('html')
    zip_codes = parser.parse_all()
    save_zip_codes('zip_code_list.txt', zip_codes)


if __name__ == '__main__':
    main()
