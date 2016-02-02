import json
import io
import unicodecsv as csv
import objectpath as op

import logging
logger = logging.getLogger(__name__)


class RawEncoder(object):

    def __init__(self, recorder, fields):
        self.recorder = recorder

    def status_handler(self, status):
        """Encodes the status to JSON string and records it."""

        self.recorder(json.dumps(status))


class FlatEncoder(object):

    def __init__(self, recorder, fields):
        self.recorder = recorder
        self.fields = self.parse_fields(fields)

    def parse_fields(self, fields):
        """Convert field list into list of key, objectpath selection tuples."""
        tuplelist = []
        for f in fields:
            k,v = f.split('=', 1)
            tuplelist.append((k.strip(), v.strip()))

        return tuplelist

    def status_handler(self, status):
        """Encodes the desired fields into flat JSON dict and records it."""

        if 'text' not in status:
            return True
        tree = op.Tree(status)
        d = {k: tree.execute(f) for k,f in self.fields}
        self.recorder(json.dumps(d))


class CSVEncoder(object):
    """ 
    The BytesIO (like StringIO) is used to capture the CSV writer output
    line-by-line prior to be recorded.
    """

    def __init__(self, recorder, fields, delimiter=',', quoting='nonnumeric'):
        self.recorder = recorder
        self.fields = self.parse_fields(fields)
        self.line = io.BytesIO()
        if isinstance(delimiter, int):
            delimiter = chr(delimiter)
        self.writer = csv.writer(self.line, 
                delimiter=delimiter, quoting=self._quote_(quoting))

    def _quote_(self, qstring):
        qtypes = dict(
            none=csv.QUOTE_NONE,
            minimal=csv.QUOTE_MINIMAL,
            nonnumeric=csv.QUOTE_NONNUMERIC,
            all=csv.QUOTE_ALL
            )
        if qstring not in qtypes:
            logger.warn('unknown csv quoting type %s', qstring)
        return qtypes.get(qstring, csv.QUOTE_NONNUMERIC)


    def parse_fields(self, fields):
        """Convert field list into objectpath selection list."""
        return [ f.split('=', 1)[1].strip() for f in fields ]


    def status_handler(self, status):
        """Encodes the desired fields into CSV and records it."""
    
        # skip deletes and limits
        if 'text' not in status:
            return True

        # convert the status (dict) into a objectpath
        tree = op.Tree(status)

        # extract the desired fields from the status
        row = [tree.execute(f) for f in self.fields]

        # remove new lines from strings
        # TODO: should this be an option?
        for i,v in enumerate(row):
            if isinstance(v, basestring):
                row[i] = v.replace('\n', ' ')

        # write the row in CSV format into a buffer
        self.writer.writerow(row)

        # write the resulting string to the recorder
        self.recorder(self.line.getvalue().strip())

        # reset line buffer
        self.line.truncate(0)
        self.line.seek(0)

        return True


def Encoder(recorder, config):
    """return an Encoder class based on configuration."""

    _format = config.get('format', 'raw')
    if _format == 'raw':
        return RawEncoder(recorder, config['fields'])
    elif _format == 'flat':
        return FlatEncoder(recorder, config['fields'])
    elif _format == 'csv':
        delimiter = config.get('delimiter', ',')
        quoting = config.get('quoting', 'minimal')
        return CSVEncoder(recorder, config['fields'],
                delimiter=delimiter, quoting=quoting)
    else:
        raise RuntimeError('unknown recorder format = %s' % _format)


