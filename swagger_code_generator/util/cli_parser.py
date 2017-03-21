# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from argparse import ArgumentTypeError
from os.path import abspath
from os.path import exists
from os.path import expanduser

from six.moves.urllib.error import URLError
from six.moves.urllib.parse import urlparse
from six.moves.urllib.request import urlopen


def path_or_uri_type(value):
    scheme, _, _, _, _, _ = tuple(urlparse(value))
    if not scheme:
        try:
            return 'file://' + path_type(value)
        except ArgumentTypeError:
            raise ArgumentTypeError("{} is not a valid URL or PATH".format(value))

    try:
        urlopen(value)
    except URLError:
        raise ArgumentTypeError("{} is not reachable".format(value))
    return value


def path_type(value):
    value = abspath(expanduser(value))
    if not exists(value):
        raise ArgumentTypeError("Path '{}' does not exist".format(value))
    return value
