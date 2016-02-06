#!/usr/bin/env python
"""
docs
"""
import os
import sys
from datetime import timedelta
import time
import json
import logging


def calc_interval(timestr):
    """ Given a *timestr* (string) such as '5d', returns a timedelta object
    representing the given value (e.g. timedelta(days=5)).
    """

    num = int(strip(timestr[:-1]))
    if timestr[-1] == 's':
        return timedelta(seconds=num)
    elif timestr[-1] == 'm':
        return timedelta(minutes=num)
    elif timestr[-1] == 'h':
        return timedelta(hours=num)
    elif timestr[-1] == 'd':
        return timedelta(days=num)


class Statistics(object):

    def __init__(self, config=None):
        if config:
            self.recorder(config)
        self.stats = dict(
            count = 0,
            coords = 0,
            deletes = 0,
            tweets = 0,
            retweets = 0,
            places = 0,
            limit = 0,
            track = 0,
            )


    def recorder(config):
        if config['mode'] == 'csv':
            pass
        elif config['mode'] == 'json':
            pass
        elif config['mode'] == 'elasticsearch':
            pass
        else:
             RuntimeError('unknown stats mode in config', config['mode'])

    def reset(self):
        for k in self.stats.keys():
            self.stats[k] = 0


    def status_handler(self, status):
        """Examines the status (tweet) and records statistics."""

        self.stats['count'] += 1
        if 'text' in status:
            self.stats['tweets'] += 1

            if 'retweeted_status' in status:
                self.stats['retweets'] += 1

            if status.get('coordinates', {}):
                self.stats['coords'] += 1

            if status.get('place', {}):
                self.stats['places'] += 1

        elif 'delete' in status:
            self.stats['deletes'] += 1 

        elif 'limit' in status:
            self.stats['limit'] += 1 
            self.stats['track'] += status['limit']['track']

        else:
            logging.warn('unknown status %s', status)

        return True


    def dumps(self, **extras):
        extras.update(self.stats)
        json.dumps(extras)

    def report(self):
        print
        print "status messages =", self.stats['count']
        print "total tweets =", self.stats['tweets']
        print "retweets =", self.stats['retweets'],
        print "(%f)" % (float(self.stats['retweets']) / self.stats['tweets'])
        print "coordinatess =", self.stats['coords'],
        print "(%f)" % (float(self.stats['coords']) / self.stats['tweets'])
        print "limit hit", self.stats['limit'],
        print "missing", self.stats['track']
