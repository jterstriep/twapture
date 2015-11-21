#!/usr/bin/env python
"""
docs
"""
from __future__ import absolute_import, print_function
import os
import time
import json

import logging
logger = logging.getLogger(__name__)


class TwitterStreamStats:

    def __init__(self, repeats=False):
        self.repeats = repeats
        self.reset()
        self.ids = {}

    def reset(self):
        self.count = 0
        self.coords = 0
        self.deletes = 0
        self.tweets = 0
        self.retweets = 0
        self.places = 0
        self.limits = 0

    def counts(self):
        return ', '.join((str(self.count), str(self.tweets),
                 str(self.retweets), str(self.coords), str(self.places)))

    def report(self):

        if self.count == 0:
            print('no tweets collected')
            return

        self.end = time.clock()

        print('total stream count = ', self.count,
              'in %f seconds' % (self.end - self.begin))
        print('total tweets = ', self.tweets,
              ' %.2f%% in stream' % (float(self.tweets)/self.count*100))
        print('total retweets = ', self.retweets, 
              ' %.2f%% of tweets' % (float(self.retweets)/self.tweets*100),
              ' %.2f%% in stream ' % (float(self.retweets)/self.count*100))
        print('total coords = ', self.coords, 
              ' %.2f%% of tweets' % (float(self.coords)/self.tweets*100),
              ' %.2f%% in stream ' % (float(self.coords)/self.count*100))
        print('total places = ', self.places, 
              ' %.2f%% of tweets' % (float(self.places)/self.tweets*100),
              ' %.2f%% in stream ' % (float(self.places)/self.count*100))
        if self.repeats:
            print('total repeats = ', sum(self.repeats.values()) - self.tweets)
        print('total deletes = ', self.deletes,
              ' %.2f%% in stream' % (float(self.deletes)/self.count*100))
        print('limits = ', self.limits,
              ' %.2f%% in stream' % (float(self.limits)/self.count*100))
        print('unknowns = ', 
            self.count - self.tweets - self.limits - self.deletes)


    def classify(self, status):

        # begin timer that ends when reporting
        if self.count == 0:
            self.begin = time.clock()

        self.count += 1
        if 'text' in status:
            print(json.dumps(status, indent=4, separators=(',', ': ')))
            self.tweets += 1

            if 'retweeted_status' in status:
                self.retweets += 1

            if status.get('coordinates', {}):
                self.coords += 1

            if status.get('place', {}):
                self.places += 1

            if self.repeats:
                self.ids[status['id_str']] = \
                    self.ids.setdefault(status['id_str'], 0) + 1

        elif 'delete' in status:
            self.deletes += 1 

        elif 'limits' in status:
            self.limits += 1 

        else:
            logger.warn('unknown status %s', status)

        return True

