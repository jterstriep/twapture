FROM python:2.7
MAINTAINER Jeff Terstriep <jefft@illinois.edu>

RUN mkdir /apt
COPY . /apt
WORKDIR /apt

RUN python setup.py install
CMD ["twapture", "--help"]
