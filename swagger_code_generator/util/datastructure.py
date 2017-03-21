# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict


class frozendict(dict):
    def __setattr__(self, key, value):
        raise NotImplementedError('Invalid operation')

    def __setitem__(self, key, value):
        raise NotImplementedError('Invalid operation')


class abstractclassmethod(classmethod):
    """
    abstract class method decorator
    Source: http://stackoverflow.com/a/11218474
    """
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


def sorteddict(dictionary):
    """
    Returns a new copy of the dictionary with sorted keys
    """
    result = OrderedDict()
    for key in sorted(dictionary):
        result[key] = dictionary[key]
    return result
