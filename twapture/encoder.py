import json
import io
import unicodecsv as csv
import objectpath as op


class RawEncoder(object):

    def __init__(self, recorder, fields):
        self.recorder = recorder

    def encode(self, status):
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

    def encode(self, status):
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

    def __init__(self, recorder, fields, 
                 delimiter=',', quoting=csv.QUOTE_NONNUMERIC):
        self.recorder = recorder
        self.fields = self.parse_fields(fields)
        self.line = io.BytesIO()
        self.writer = csv.writer(self.line, 
                delimiter=delimiter, quoting=quoting)

    def parse_fields(self, fields):
        """Convert field list into objectpath selection list."""
        return [ f.split('=', 1)[1].strip() for f in fields ]

    def encode(self, status):
        """Encodes the desired fields into CSV and records it."""
    
        # skip deletes and limits
        if 'text' not in status:
            return True

        # convert the status (dict) into a objectpath
        tree = op.Tree(status)

        # extract the desired fields from the status
        row = [tree.execute(f) for f in self.fields]

        # write the row in CSV format into a buffer
        self.writer.writerow(row)

        # write the resulting string to the recorder
        self.recorder(self.line.getvalue().strip())

        # reset line buffer
        self.line.truncate(0)
        self.line.seek(0)

        return True

