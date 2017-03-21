# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from random import random

import pytest
from six import iteritems
from six.moves import xrange

from swagger_code_generator.generator_metaclass import AbstractLanguageGenerator
from swagger_code_generator.util.datastructure import frozendict


def test_frozendict_equivalent_to_dict():
    objects = {key: random() for key in xrange(10)}
    assert frozendict(objects) == objects


def test_frozendict_not_allow_item_writings():
    with pytest.raises(NotImplementedError):
        frozendict({})['key'] = 'value'


def test_frozendict_not_allow_attribute_writings():
    with pytest.raises(NotImplementedError):
        frozendict({}).attr = 'value'


def test_not_instantiate_class():
    class LanguageGenerator(AbstractLanguageGenerator):
        pass

    with pytest.raises(TypeError) as exception_info:
        LanguageGenerator()

    # Code extracted from abc library
    abstract_methods = sorted(
        name
        for name, value in iteritems(AbstractLanguageGenerator.__dict__)
        if getattr(value, '__isabstractmethod__', False)
    )
    assert exception_info.value.args == (
        'Can\'t instantiate abstract class {} with abstract methods {}'.format(
            LanguageGenerator.__name__,
            ', '.join(abstract_methods),
        ),
    )
