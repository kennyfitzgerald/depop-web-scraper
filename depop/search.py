# Standard library imports
import pandas as pd
import time
import re
from bs4 import BeautifulSoup as bs
import requests
import winsound
import webbrowser
import socket
import datetime
from threading import *
import threading


# Local library imports
import depop.config as cf


# Defining base URLs
BASE_SEARCH_URL = 'https://www.depop.com/search/?q='
BASE_PROD_URL = 'https://www.depop.com/products/'


class Search:

    """
    This class is built to run search queries as defined in the search_config.ini file.

    """

    def __init__(self, query, sizes, min_price, max_price, interval, filter_desc, blacklist_users):

        self.query = query
        self.sizes = sizes
        self.min_price = min_price
        self.max_price = max_price
        self.interval = interval
        self.filter_desc = filter_desc
        self.blacklist_users = blacklist_users

        self.screenlock = Semaphore(value=1)

    def _is_connected(self):

        """ Checks for internet connection.
            Returns:
                is_connected: Boolean returing True if connected and False if not.
        """

        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection(("1.1.1.1", 53))
            return True

        except OSError:
            pass

        return False


    def _get_search_results(self):

        """ Takes the search query as input and returns a beautifulsoup object of the results
        """

        # Create search URL object using term defined above and pull from site.
        URL = BASE_SEARCH_URL + re.sub(" ", "-", self.query)

        self._running_string('RUNNING...')

        while True:
            try:
                page = requests.get(URL)
                soup = bs(page.content, 'html.parser')
                results = soup.find(id='main')
                query_results = results.find_all('li', class_='styles__ProductCardContainer-sc-5cfswk-7 eJFfoL')
                break

            except:
                time.sleep(5)
                pass

        return(query_results)


    def _get_element_details(self, element):

        """ Takes an element of search query results and returns a list of price, user, reference and link """

        price = float(re.sub("[^0-9.]", "", element.find_all('span')[-1].text))
        user = re.sub("item listed by ", "", element.find('img')['alt'])
        ref = re.findall(r'' + user + '-(.+?)/', element.find_all('a')[0]['href'])[0]
        url = BASE_PROD_URL + user + '-' + ref

        # Combine item details into list
        element_details = list([ref, user, price, url])
        return(element_details)


    def _parse_most_recent_item(self, query_results):

        """ Takes the query results and returns a list of details of the most recent object """
        element = query_results[0]
        most_recent_item_details = self._get_element_details(element)
        return(most_recent_item_details)


    def _get_further_item_details(self, url):

        """ Takes an item URL and returns additional details: size, condition, date, time, description, image link """

        # Get item page html
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')
        results = soup.find()

        # Extract description from item page
        description = results.find('p', class_='Text-yok90d-0 styles__DescriptionContainer-uwktmu-9 bWcgji')
        if(description == None):
            return([])
        else:
            description = description.text

        # Extract the element containing size
        size_element = results.find_all('td', class_='TableCell-zjtqe7-0 eTPofW')

        # Extract size from size element
        if(len(size_element) in [0, None]):
            return([])
        elif(len(size_element) == 1):
            size = ""
        else:
            size = size_element[1].text

        # Retrieves condition data
        condition = results.find(attrs={'data-testid': 'product__condition'})

        # If a condition has been stated then it is stored. If not then it is left empty.
        if (condition == None):
            condition = ""
        else:
            condition = condition.text

        # Retrieving date and time objects.
        date_time = results.find('time', attrs={'class', 'Time-pkm14p-0 dFgHcz'})
        date = date_time['datetime'][0:10]
        time = date_time['datetime'][11:19]

        # And a link to the main image.
        image_url = results.find('meta', attrs={'property': 'og:image'})
        image_url = image_url['content']

        # Compiling output into a list.
        further_item_details = list([size, condition, date, time, description, image_url])
        return(further_item_details)


    def _filter_description(self, description):

        """ Takes a description and the set of defined blacklisted terms, then results True if the description
        contains any of the listed terms. """

        description = re.sub('/n', ' ', description)
        description = re.sub(' +', ' ', description)
        description = description.lower()

        res = [ele for ele in self.filter_desc if (ele in description)]

        return (bool(res))


    def _get_all_item_details(self, query_results):

        # Empty dataframe to store results in.
        all_items = pd.DataFrame(columns=['ref', 'user', 'price', 'url', 'size', 'condition', 'date', 'time',
                                          'description', 'image_url'])

        for element in query_results:

            # Get ref, user, price and url
            element_details = self._get_element_details(element)

            # ignore element if max price is exceeded
            if(element_details[2] > self.max_price):
                continue

            # ignore element if user is blacklisted
            if(element_details[1] in self.blacklist_users):
                continue

            # Retrieve further item details
            full_element_details = element_details + self._get_further_item_details(element_details[3])

            # If item search has failed (item no longer listed) then skip.
            if(len(full_element_details) == 4):
                continue

            # Check if item is within range of sizes
            if(full_element_details[4] not in self.sizes):
                continue

            # Check item price is not equal to 1
            if(full_element_details[2] == 1):
                continue

            # Check that the description does not contain blacklisted terms
            if(self._filter_description(full_element_details[8]) == True):
                continue

            # If element has passed all above checks then it matches the criteria and is added to the pandas dataframe
            a_series = pd.Series(full_element_details, index = all_items.columns)

            all_items = all_items.append(a_series, ignore_index=True)

        return(all_items)


    def _filter_new_rows_only(self, items, old_items):

        """ Takes as input a dataframe of new items and a dataframe of the previous search, then returns rows from the
            new search that are not present in the old search
        """

        empty_df = pd.DataFrame(columns=['ref', 'user', 'price', 'url', 'size', 'condition', 'date', 'time',
                                          'description', 'image_url'])

        if items.equals(empty_df):
            return(items)

        if items.equals(old_items):
            return(empty_df)

        if old_items is None:
            return(items)

        new_rows_only = \
            pd.merge(items, old_items, how='outer', indicator=True)\
            .query('_merge=="left_only"')\
            .drop('_merge', 1)

        return(new_rows_only)


    def _open_new_items_in_browser_and_beep(self, urls):

        """ Takes a list of urls as input and opens them all. Also sends beep notification. """
        winsound.Beep(1000, 700)
        for url in urls:
            webbrowser.open(url)


    def _running_string(self, string_end):
        print(datetime.datetime.now().strftime("%H:%M:%S")
              + ' - ' + self.query
              + '/['
              + ', '.join(self.sizes)
              + ']/'
              + str(self.min_price) + '-' + str(self.max_price)
              + ' ' + string_end)


    def _run_search(self, query_results, old_items):

        """ Runs a search using the query and parameters specified in the payload and returns a pandas dataframe of
            items matching the criteria.
            """

        # Scan search results object to produce a dataframe of all item details that match criteria
        items = self._get_all_item_details(query_results)

        # Filter only new rows
        new_items = self._filter_new_rows_only(items, old_items)

        # Print items if any are found.
        if (len(new_items.index) > 0):

            self.screenlock.acquire()
            self._running_string('ITEMS FOUND:')
            print(new_items[['ref', 'price']])
            self.screenlock.release()
            self._open_new_items_in_browser_and_beep(new_items['url'])

        else:

            self._running_string('NO ITEMS FOUND.')

        return(items)


    def run_timed_search(self):

        """ Begins continuously scraping the depop website for the specified search query at an interval defined
            in the configuration file. """

        starttime = time.time()
        query_results = self._get_search_results()
        first_item = self._parse_most_recent_item(query_results)
        items = self._run_search(query_results, old_items=None)

        while True:

            time.sleep(self.interval - ((time.time() - starttime) % self.interval))
            query_results = self._get_search_results()
            new_first_item = self._parse_most_recent_item(query_results)

            if(new_first_item == first_item):
                self._running_string('NO ITEMS FOUND.')
                continue
            else:
                first_item = new_first_item
                old_items = items
                items = self._run_search(query_results, old_items)

