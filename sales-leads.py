
__author__ = 'Adetola'
"""
Uses to YELP API to get search results and

"""

import argparse
import json
import pprint
import sys
import urllib
import urllib2

import oauth2
import re
import unicodedata
import math


API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'transportation'
DEFAULT_LOCATION = 'Washington, DC'
SEARCH_LIMIT = 20
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'
DEFAULT_FILE = 'test.json'
DEFAULT_TOTAL = 61


# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = '85_UhVhnDO4VfffFxcHsEw'
CONSUMER_SECRET = 'n7mlt1alyUIXQDMsrmFNqbeS0R4'
TOKEN = 'pFHxGk7i_AZSLYXwpia3S9KNJpgkDnC0'
TOKEN_SECRET = 'nCVuII3qO8uPKVIceUQvZRtbyb8'


def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print 'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        # Convert json string to json
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location, offset):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset': offset

    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def get_business(business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path)

def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """

    leads_file = open(DEFAULT_FILE, 'wb+')
    number_of_searches = int(math.ceil(DEFAULT_TOTAL/20))


    for search_number in xrange(number_of_searches):

        offset = (search_number - 1 ) * DEFAULT_TOTAL
        if(offset < 1):
            response = search(term, location, 1)
        else:
            response = search(term, location, offset)




        businesses = response.get('businesses')

        if not businesses:
            print 'No businesses for {0} in {1} found.'.format(term, location)
            return

        print '{0} businesses found" ...'.format(
            len(businesses)
        )




        for business in businesses:

            business_lead = business['location'] if business.get("location") else ""


            business_lead['name'] = business['name'] if business.get("name") else ""
            business_lead['phone'] = business['phone'] if business.get("phone") else ""
            business_lead['url']= business['url'] if business.get("url") else ""

            # Converts json to string
            line = json.dumps(business_lead)

            leads_file.write(line+"\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM, type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location', default=DEFAULT_LOCATION, type=str, help='Search location (default: %(default)s)')
    parser.add_argument('-f', '--file', dest='file', default=DEFAULT_FILE, type=str, help='Search location (default: %(default)s)')
    parser.add_argument('-t', '--total', dest='total', default=DEFAULT_TOTAL, type=int, help='Total Number of Results (default: %(default)d)')



    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.location)
    except urllib2.HTTPError as error:
        sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))


if __name__ == '__main__':
    main()

