#!/usr/bin/env python
"""
The MultiplexListener passes each status through a series of filters
stopping when one of them returns False. Several sample filters are
provided.

Author: Jeff Terstriep
Date: 11/20/2015

"""
import json
import logging
logger = logging.getLogger(__name__)

from tweepy.streaming import StreamListener


def only_coords(status):
    """ only allow tweets with coordinates """
    if 'text' in status and status.get('coordinates', {}):
        return True
    else:
        return False

def block_non_tweets(status):
    """ block non-tweets such as delete and limit objects """
    if 'delete' in status or 'limit' in status:
        return False

def block_retweets(status):
    """ eliminate retweets """
    if 'text' in status and 'retweeted_status' in status:
        return False

def pprint_tweets(status):
    """ pretty print status to stdout """
    print json.dumps(status, indent=4, separators=[',', ': '])
    return True


class MultiplexListener(StreamListener):
    """ The multiplex listener takes a list of one or more functions
        and passes the status during the callback. Care must be taken
        maintain the data stream.
    """

    def __init__(self, *multiplex):
        super(MultiplexListener, self).__init__()
        self.multiplex = multiplex

    def on_data(self, data):
        status = json.loads(data)

        # stop processing functions when False is returned
        for func in self.multiplex:
            if not func(status):
                break

        return True

    def on_error(self, status):
        if status == 420:
            logger.warn('MultiplexListener: twitter stream is being limited')
            return True

        # twitter server errors
        elif status >= 500:
            logger.error('MultiplexListener: twitter server error: code=%d',
                         status)
            return True

        else:
            logger.error('MultiplexListener: stream returned error: code=%d',
                         status)
            return True
