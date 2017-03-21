# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
from bravado_core.spec import Spec

from swagger_code_generator.generator_metaclass import AbstractLanguageGenerator


BASE_PACKAGE = 'swagger_code_generator'


@pytest.yield_fixture
def mock_MetaClassRegistry():
    with mock.patch(BASE_PACKAGE + '.main.MetaClassRegistry', autospec=True) as _mock:
        _mock.__repr__ = lambda self: 'MetaClassRegistry'
        _mock.registry_classes.return_value = frozenset()
        yield _mock


@pytest.yield_fixture
def mock_LanguageGenerator(mock_MetaClassRegistry):
    _mock = mock.MagicMock(AbstractLanguageGenerator, autospec=True)
    _mock.language.return_value = 'language'
    _mock.subparser_help.return_value = 'sub-parser help'
    mock_MetaClassRegistry.registry_classes.return_value = frozenset(
        list(mock_MetaClassRegistry.registry_classes.return_value) + [_mock]
    )
    yield _mock


@pytest.fixture
def minimal_swagger_dict():
    return {
        'swagger': '2.0',
        'info': {
            'title': 'Test',
            'version': '1.0',
        },
        'paths': {
        },
        'definitions': {
        },
    }


@pytest.fixture
def minimal_swagger_spec(minimal_swagger_dict):
    return Spec.from_dict(minimal_swagger_dict)
