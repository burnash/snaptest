#!/usr/bin/env python

import os
import sys

import json

import urlparse
import argparse
import requests
import unittest


SNAP_DIRNAME = '.snaptest'


class ResponseTest(unittest.TestCase):

    def __init__(self, testname, local_data, remote_data):
        super(ResponseTest, self).__init__(testname)
        self.local_data = local_data
        self.remote_data = remote_data

    def test_equal(self):
        self.assertEqual(self.local_data, self.remote_data)


def get_local_name(url):
    parsed = urlparse.urlparse(url)
    path_parts = [s for s in parsed.path.split('/') if s]
    path_parts.insert(0, parsed.netloc)
    if parsed.query:
        path_parts.append(parsed.query)
    path_parts.append('json')

    return os.path.join(SNAP_DIRNAME, ".".join(path_parts))


def read_url(url):
    r = requests.get(url)

    return r.json()


def write_data(filename, data):
    if not os.path.exists(SNAP_DIRNAME):
        os.makedirs(SNAP_DIRNAME)

    filename = os.path.join(SNAP_DIRNAME, filename)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def main():
    parser = argparse.ArgumentParser(
        description='Memorize and compare http responses')

    parser.add_argument('url', metavar='URL', help='url to fetch')

    args = parser.parse_args()

    filename = get_local_name(args.url)

    try:
        f = open(filename)
        print "reading", filename, '...'
        local_data = json.load(f)

        remote_data = read_url(args.url)

        suite = unittest.TestSuite()
        suite.addTest(ResponseTest("test_equal", local_data, remote_data))
        unittest.TextTestRunner().run(suite)

    except IOError:
        print filename, 'not found. reading url'

        data = read_url(args.url)
        write_data(filename, data)

    sys.exit(0)

if __name__ == "__main__":
    main()
