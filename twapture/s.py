#!/usr/bin/env python
#Author: Jeff Terstriep
#Date: 11/20/2015
"""
The SerializedListener passes each status through a series of filters 
(functions) stopping when one of them returns False. Several sample
filters are provided.
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


class SerializedListener(StreamListener):
    """ The serialized listener takes a list of one or more functions
        and passes the status during the callback. Care must be taken
        maintain the data stream.
    """

    def __init__(self, *functions):
        super(SerializedListener, self).__init__()
        self.functions = list(functions)

    def __len__(self):
        return len(self.functions)

    def __getitem__(self, key):
        return self.functions[key]

    def __setitem__(self, key, value):
        return self.functions[key] = value

    def __delitem__(self, key):
        del self.functions[key]

    def __iter__(self):
        return iter(self.functions)

    def append(self, value):
        self.functions.append(value)

    def on_data(self, data):
        status = json.loads(data)

        # stop processing functions when False is returned
        for func in self.functions:
            if not func(status):
                break

        return True

    def on_error(self, status):
        if status == 420:
            logger.warn('SerializedListener: twitter stream is being limited')
            return True

        # twitter server errors
        elif status >= 500:
            logger.error('SerializedListener: twitter server error: code=%d',
                         status)
            return True

        else:
            logger.error('SerializedListener: stream returned error: code=%d',
                         status)
            return True
