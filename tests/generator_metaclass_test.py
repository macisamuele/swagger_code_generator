# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
from bravado_core.spec import Spec
from six import add_metaclass

from swagger_code_generator.generator_metaclass import AbstractLanguageGenerator
from swagger_code_generator.generator_metaclass import MetaClassRegistry
from tests.conftest import BASE_PACKAGE


@pytest.yield_fixture
def language_generator_class():
    class LanguageGenerator(AbstractLanguageGenerator):
        render = mock.MagicMock()
        set_subparser = mock.MagicMock()
        language = mock.MagicMock()
        validate_args = mock.MagicMock()

    return LanguageGenerator


@pytest.yield_fixture
def registered_language_generator_class(language_generator_class):
    yield add_metaclass(MetaClassRegistry)(language_generator_class)


def test_no_registered_class(language_generator_class):
    assert MetaClassRegistry.registry() == {}
    assert MetaClassRegistry.registry_classes() == frozenset()
    assert MetaClassRegistry.registry_keys() == frozenset()


def test_registered_class(registered_language_generator_class):
    assert MetaClassRegistry.registry() == {
        '{}.{}'.format(
            test_no_registered_class.__module__,
            registered_language_generator_class.__name__,
        ): registered_language_generator_class,
    }
    assert MetaClassRegistry.registry_classes() == frozenset([registered_language_generator_class])
    assert MetaClassRegistry.registry_keys() == frozenset(['{}.{}'.format(
        test_no_registered_class.__module__,
        registered_language_generator_class.__name__,
    )])


@pytest.mark.parametrize(
    'operations', (True, False,),
)
@mock.patch(BASE_PACKAGE + '.generator_metaclass.get_operations_to_render', autospec=True)
@mock.patch(BASE_PACKAGE + '.generator_metaclass.get_models_to_render', autospec=True)
def test_language_generator_run(
    mock_get_models_to_render, mock_get_operations_to_render,
    language_generator_class, operations,
):
    mock_swagger_spec = mock.Mock(spec=Spec)
    mock_args = mock.MagicMock(operations=operations)

    mock_language_generator = language_generator_class
    mock_language_generator.run(mock_swagger_spec, mock_args)

    mock_get_models_to_render.assert_called_once_with(mock_swagger_spec)
    if operations:
        mock_get_operations_to_render.assert_called_once_with(mock_swagger_spec, mock_get_models_to_render.return_value)
    else:
        assert not mock_get_operations_to_render.called

    mock_language_generator.render.assert_called_once_with(
        swagger_spec=mock_swagger_spec,
        models_to_render=mock_get_models_to_render.return_value,
        operations_to_render=mock_get_operations_to_render.return_value if operations else (),
        args=mock_args,
    )
