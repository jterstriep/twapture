# Description: flexibly capture twitter streams using python logging
# Author: Jeff Terstriep <jterstriep@gmail.com>
# Date: 11/19/2015
# License: NCSA Open Source
import sys
import logging

logger = logging.getLogger(__name__)


def config_stream_recorder(xlog, stream, level=logging.INFO):
    xlog.propagate = False
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter('%(message)s')
    xlog.addHandler(handler)
    xlog.setLevel(level)


def config_watched_recorder(xlog, fname, bufsize):
    """Creates a xlog with an in-memory handler that feeds a watched
       file handler.
    """
    xlog.propagate = False
    handler = logging.handlers.WatchedFileHandler(fname)
    handler.setLevel(logging.INFO)
    memhandler = logging.handlers.MemoryHandler(bufsize, target=handler)
    memhandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    memhandler.setFormatter(formatter)
    xlog.addHandler(memhandler)
    xlog.setLevel(logging.INFO)


def config_timed_recorder(xlog, fname, interval, bufsize):
    """Creates a xlog with an in-memory handler that acts as a buffer
       for a timed rotator file handler.
    """
    xlog.propagate = False
    if interval in ('midnight', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6'):
        handler = logging.handlers.TimedRotatingFileHandler(fname, when=interval)
    else:
        value,units = int(interval[:-1]), interval[-1]
        handler = logging.handlers.TimedRotatingFileHandler(fname, 
                when=units, interval=value)

    memhandler = logging.handlers.MemoryHandler(bufsize, target=handler)
    formatter = logging.Formatter('%(message)s')
    memhandler.setFormatter(formatter)
    xlog.addHandler(handler)
    xlog.setLevel(logging.INFO)


def config_recorder(xlog, fname, interval, bufsize=100):
    """Configures a xlog for recording series data. 

    The xlog can use stream writing (stdout or stderr) or to
    a watched or rotating file log type. Watched log file is used if
    if no interval is given.
    """

    if not fname:
        raise RuntimeError('file name is required for data recorder')

    if fname == 'stdout':
        config_stream_recorder(xlog, sys.stdout)
    elif fname == 'stderr':
        config_stream_recorder(xlog, sys.stderr)
    elif interval:
        config_timed_recorder(xlog, fname, interval, bufsize=bufsize)
    else:
        config_watched_recorder(xlog, fname, bufsize=bufsize)


class Recorder(object):
    """
    The Recorder class creates a data recorder using Python's rather
    excellent logging facility. 

    The class includes a status_handler to be used as a callback in
    the twitter API. The status is first passed through an encoder
    function and then written to the log.
    """

    def __init__(self, name, **config):
        self.name = name
        self.encoder = config.get('encoder', self.dumps)
        self.recorder = logging.getLogger(name)
        config_recorder(
                self.recorder, 
                config.get('filename', 'stdout'),
                config.get('rotating', None), 
                config.get('buffer-size', 100),
                )

    def status_handler(self, status):
        record = self.encoder(status)
        if record:
            self.recorder.info(record)
        return True


    def dumps(self, status):
        """default encoder converts status into json string"""
        return json.dumps(status)

