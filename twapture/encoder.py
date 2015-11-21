import os
import sys
import json

import logging
logger = logging.getLogger(__name__+'.encoder')


class StatusEncoder:

    def __init__(self, recorder, delimiter=','):
        self.recorder = recorder
        self.delimiter = delimiter

    def get_longitude(self, status, default='0.0'):
        c = status.get('coordinates', {})
        if not c:
            return default
        else:
            return str(c.get('coordinates')[0])
    
    def get_latitude(self, status, default='0.0'):
        c = status.get('coordinates', {})
        if not c:
            return default
        else:
            return str(c.get('coordinates')[1])

    def get_latlong(self, status, default=['0.0', '0.0']):
        """ return coordinate list in lat, long order
            Note: most tweets don't have coords set
        """
        c = status.get('coordinates', {})
        if c:
            return [str(c.get('coordinates')[1]), str(c.get('coordinates')[0])]
        else:
            return default

    def is_retweet(self, status):
        return str('retweeted_status' in status).lower()


    def encode(self, status):
        """encodes the results into a string for writing to recorder"""
    
        # skip deletes and limits
        if 'text' not in status:
            return True

        user = status.get('user', {})
        place = status.get('place', {})
        if place == None:
            place = {}
        ostatus = status.get('retweeted_status', {})
        if ostatus == None:
            ostatus = {}

        fields = [
            status.get('text', ''),
            status.get('id_str', ''),
            status.get('created_at', ''),
            status.get('source', ''),
            self.is_retweet(status),
            self.get_latitude(status),
            self.get_longitude(status),
            user.get('id_str', ''),
            user.get('name', ''),
            place.get('id', ''),
            place.get('name', ''),
            place.get('place_type', '')
            ]
        
        self.recorder(self.delimiter.join(fields))
        return True

