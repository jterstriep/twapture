# Description: flexibly capture twitter streams using python logging
# Author: Jeff Terstriep <jterstriep@gmail.com>
# Date: 11/19/2015
# License: NCSA Open Source

import logging


def config_stdout_recorder(logger, level=logging.INFO):
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def config_watched_recorder(logger, fname, bufsize=100, level=logging.INFO):
    """Creates a logger with an in-memory handler that feeds a watched
       file handler.
    """
    handler = logging.handlers.WatchedFileHandler(fname)
    handler.setLevel(logging.INFO)
    memhandler = logging.handlers.MemoryHandler(bufsize, target=handler)
    memhandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    memhandler.setFormatter(formatter)
    logger.addHandler(memhandler)
    logger.setLevel(logging.INFO)


def config_timed_recorder(logger, fname, interval, bufsize=100, backupCount=0):
    """Creates a logger with an in-memory handler that acts as a buffer
       for a timed rotator file handler.
    """
    if interval in ('midnight', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6'):
        handler = logging.handlers.TimedRotatingFileHandler(fname, 
                when=interval, backupCount=backupCount)
    else:
        value,units = int(interval[:-1]), interval[-1]
        handler = logging.handlers.TimedRotatingFileHandler(fname, 
                when=units, interval=value, backupCount=backupCount)

    memhandler = logging.handlers.MemoryHandler(bufsize, target=handler)
    formatter = logging.Formatter('%(message)s')
    memhandler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class Recorder(object):

    def __init__(self, config, encoder):
        self.encoder = encoder
        self.fname = config.get('filename', 'stdout')
        self.rotating = config.get('rotating', 'none')
        self.bufsize = config.get('buffer-size', 100)
        self.recorder = logging.getLogger(u'tweet_recorder')

        if self.fname == 'stdout':
            config_stdout_recorder(self.recorder)
        elif rotation == 'none':
            config_watched_recorder(self.recorder, self.fname, 
                    bufsize=self.bufsize)
        else:
            config_timed_recorder(self.recorder, self.fname, 
                    self.rotation, bufsize=self.bufsize)

    def status_handler(self, status):
        self.recorder.info(self.encoder(status))

