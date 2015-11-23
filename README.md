# Twapture - capturing tweets using Twitter's streaming API
Twapture provides a flexible tool for capturing tweets from Twitter's
streaming API.  The stream can be filtered based on topics (keywords 
and phrases) and/or location (bounding box). If no filters are specified
the entire public data stream is sampled.

With no options, twapture dumps all incoming tweets to stdout in human
readable format. But, twapture uses Python's excellent logging tool to
record incoming tweets to file. By default, a WatchedFileHandler is used
so that an external process can manage file rotation, but a 
TimedRotatingFileHandling can be specified to allow twapture to 
self-manage its record files.

Twapture can be used as a command line tool to explore the twitter stream,
but it is primarily designed to work in concert with supervisord to provide
a robust, continuously running capture service.

The twapture package includes 3 custom classes; MultiplexListener, 
StatusEncoder, and TwitterStreamStats. MultiplexListener allows a
series of filtering functions to be performed on each status update.
StatusEncoder helps format a status for inclusion in files or outputing
to another service. TwitterStreamStats provides a MultiplexListener
filter that collects statistics on the incoming stream.

## Installion

```bash
git clone https://github.com/jterstriep/twapture.git
sudo python setup.py install
```

## To Do
Write documentation
Add stream statistics
Add package to Pypi


