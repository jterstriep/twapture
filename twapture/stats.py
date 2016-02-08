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
logger = logging.getLogger(__name__)

from twapture import Encoder


def calc_interval(timestr):
    """ Given a *timestr* (string) such as '5d', returns a timedelta object
    representing the given value (e.g. timedelta(days=5)).
    """

    num = int(timestr[:-1])
    if timestr[-1] == 's':
        return timedelta(seconds=num).seconds
    elif timestr[-1] == 'm':
        return timedelta(minutes=num).seconds
    elif timestr[-1] == 'h':
        return timedelta(hours=num).seconds
    elif timestr[-1] == 'd':
        return timedelta(days=num).seconds


class Statistics(object):
    """
    An pseudo-encoder class that collects statistics on tweets. This clase
    provides both an encoder and handler method.

    Inheritance from Encoder is not used because Encoder is function that
    returns one of several different encoder classes.
    """

    def __init__(self, **config):
        self.encoder = Encoder(**config)

        self.interval = 0.0
        self.trigger_time = 0.0
        if 'interval' in config:
            self.interval = calc_interval(config['interval'])
            logger.debug('stats recorded on %f secs', self.interval)
            self.trigger_time = time.time() + self.interval

        stime = time.time()
        self.stats = dict(
            start = stime,
            timestamp = time.ctime(stime),
            duration = 0.0,
            count = 0,
            tweets = 0,
            coords = 0,
            retweets = 0,
            places = 0,
            limits = 0,
            track = 0,
            deletes = 0,
            )


    def reset(self):
        for k in self.stats.keys():
            self.stats[k] = 0
        self.stats['start'] = time.time()
        self.stats['timestamp'] = time.ctime(self.stats['start'])
        if self.trigger_time:
            self.trigger_time = time.time() + self.interval


    def status_encoder(self, status):
        self.status_handler(status)

        # only return stats if trigger time has been been defined and expired
        if self.trigger_time and time.time() > self.trigger_time:
            logger.debug('stats encoder triggered')
            self.stats['duration'] = time.time() - self.stats['start']
            record = self.encoder.status_encoder(self.stats)
            self.reset()
            return record
        else:
            return ''


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
            self.stats['limits'] += 1 
            self.stats['track'] = status['limit']['track']

        else:
            logger.warn('unknown status %s', status)

        return True


    def dumps(self, **extras):
        extras.update(self.stats)
        json.dumps(extras)

    def report(self):
        print "starting at", time.ctime(self.stats['start']), 
        print "(%10.0f secs)" % self.stats['start']
        print "duration = %10.0f secs" % (time.time() - self.stats['start'])
        print "status messages =", self.stats['count']
        print "total tweets =", self.stats['tweets']
        print "retweets = {0} ({1:.0%})".format(self.stats['retweets'],
                float(self.stats['retweets']) / self.stats['tweets'])
        print "coordinates = {0} ({1:.0%})".format(self.stats['coords'],
                float(self.stats['coords']) / self.stats['tweets'])
        print "limit hit {} times, track = {}".format(self.stats['limits'],
                self.stats['track'])
