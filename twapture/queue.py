#!/usr/bin/env python
#Author: Jeff Terstriep
#Date: 11/20/2015
"""
The SerializedListener passes each status through a series of filters 
(functions) stopping when one of them returns False. Several sample
filters are provided.
"""
import json
import Queue
import logging
logger = logging.getLogger(__name__)

from twapture import SerializedListener

class TweetQueue(threading.Thread):
    """ The serialized listener takes a list of one or more functions
        and passes the status during the callback. Care must be taken
        maintain the data stream.
    """

    def __init__(self):
        self.listener = SerializedListener()

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
