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
        self.functions[key] = value

    def __delitem__(self, key):
        del self.functions[key]

    def __iter__(self):
        return iter(self.functions)

    def append(self, value):
        self.functions.append(value)

    def on_data(self, raw_data):
        status = json.loads(raw_data)

        # stop processing functions when False is returned
        for func in self.functions:
            if not func(status):
                logger.debug('pipeline ended')
                break

        return True

    def on_error(self, status):
        if status == 420:
            logger.warn('twitter stream is being limited')

        elif status == 401:
            logger.error('could not authentic, check credentials: code=401')

        # twitter server errors
        elif status >= 500:
            logger.error('twitter server error: code=%d', status)

        else:
            logger.error('stream returned error: code=%d', status)


    def on_limit(self, track):
        logger.warn('limit reach: %s', str(track))

    def on_disconnect(self, notice):
        logger.error('disconnect: %s', str(notice))

    def on_warning(self, notice):
        logger.warning('warning: %s', str(notice))

    def on_exception(self, exception):
        logger.exception('streaming exceptions: %s', str(exception))
