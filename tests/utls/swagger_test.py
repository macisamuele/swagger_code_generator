# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from swagger_code_generator.util.datastructure import sorteddict
from swagger_code_generator.util.swagger import _get_model_fields
from swagger_code_generator.util.swagger import _get_models
from swagger_code_generator.util.swagger import get_operations_to_render
from swagger_code_generator.util.swagger import SwaggerBodyModel
from swagger_code_generator.util.swagger import SwaggerModel
from swagger_code_generator.util.swagger import SwaggerResponseModel
from tests.conftest import minimal_swagger_spec


@pytest.mark.parametrize(
    'schema, expected_model_name',
    (
        ({'x-title': 'x-title'}, 'x-title',),
        ({'x-model': 'x-model'}, 'x-model',),
        ({'title': 'title'}, 'title',),
        ({'title': 'title', 'x-model': 'x-model'}, 'x-model',),
        ({'title': 'title', 'x-model': 'x-model', 'x-title': 'x-title'}, 'x-title',),
    )
)
@mock.patch.object(SwaggerModel, 'get_model_name_fallback', return_value=None)
def test_SwaggerModel_get_model_name_respect_ordering(mock_get_model_name_fallback, schema, expected_model_name):
    assert SwaggerModel(schema=schema).get_model_name == expected_model_name
    assert not mock_get_model_name_fallback.called


def test_SwaggerModel_get_model_name_fallback():
    with pytest.raises(NotImplementedError):
        SwaggerModel(schema={}).get_model_name


def test__get_models_minimal_spec(minimal_swagger_spec):
    assert _get_models(minimal_swagger_spec) == {}


def test__get_models_one_operation_no_body_no_response_schema(minimal_swagger_dict):
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'get': {
                'responses': {
                    '200': {
                        'description': 'description',
                    },
                },
            },
        },
    }
    swagger_spec = minimal_swagger_spec(minimal_swagger_dict)
    assert _get_models(swagger_spec) == {}


@pytest.mark.parametrize(
    'has_body', (True, False,),
)
@pytest.mark.parametrize(
    'has_response_definition', (True, False,),
)
def test__get_models_one_operation(
    minimal_swagger_dict, has_body, has_response_definition,
):
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'get': {
                'responses': {
                    '200': {
                        'description': 'description',
                    },
                },
            },
        },
    }
    if has_body:
        minimal_swagger_dict['paths']['/endpoint']['get'].update({
            'parameters': [
                {
                    'description': 'body object',
                    'in': 'body',
                    'name': 'body',
                    'required': True,
                    'schema': {
                        'type': 'object',
                    }
                }
            ],
        })
    if has_response_definition:
        minimal_swagger_dict['paths']['/endpoint']['get']['responses']['200'].update({
            'schema': {
                'type': 'object',
            },
        })
    swagger_spec = minimal_swagger_spec(minimal_swagger_dict)

    expected_models = []

    if has_body:
        expected_models.append(
            SwaggerBodyModel(
                schema=minimal_swagger_dict['paths']['/endpoint']['get']['parameters'][0]['schema'],
                http_method='GET',
                url='/endpoint',
            )
        )

    if has_response_definition:
        expected_models.append(
            SwaggerResponseModel(
                schema=minimal_swagger_dict['paths']['/endpoint']['get']['responses']['200']['schema'],
                http_method='GET',
                url='/endpoint',
                response_code='200',
            )
        )

    models = _get_models(swagger_spec)

    assert models == {
        model.get_model_name: model
        for model in expected_models
    }


def test__get_models_warning_multiple_models_with_same_name(
    minimal_swagger_dict,
):
    body_schema = {
        'type': 'object',
        'properties': {
            'prop': {
                'type': 'string'
            }
        },
        'x-title': 'model',
    }
    response_schema = body_schema

    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'parameters': [
                {
                    'description': 'body object',
                    'in': 'body',
                    'name': 'body',
                    'required': True,
                    'schema': body_schema,
                }
            ],
            'get': {
                'responses': {
                    '200': {
                        'description': 'description',
                        'schema': response_schema,
                    },
                },
            },
        },
    }
    swagger_spec = minimal_swagger_spec(minimal_swagger_dict)

    expected_models = [
        SwaggerBodyModel(
            schema=body_schema,
            http_method='GET',
            url='/endpoint',
        ),
    ]

    models = _get_models(swagger_spec)
    assert models == {
        model.get_model_name: model
        for model in expected_models
    }


def test__get_models_warning_different_models_with_same_name(
    minimal_swagger_dict,
):
    body_schema = {
        'type': 'object',
        'properties': {
            'prop': {
                'type': 'string'
            }
        },
        'x-title': 'model',
    }
    response_schema = {
        'type': 'object',
        'properties': {
            'prop': {
                'type': 'integer'
            }
        },
        'title': 'model',
    }

    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'parameters': [
                {
                    'description': 'body object',
                    'in': 'body',
                    'name': 'body',
                    'required': True,
                    'schema': body_schema,
                }
            ],
            'get': {
                'responses': {
                    '200': {
                        'description': 'description',
                        'schema': response_schema,
                    },
                },
            },
        },
    }
    swagger_spec = minimal_swagger_spec(minimal_swagger_dict)

    expected_models = [
        SwaggerBodyModel(
            schema=body_schema,
            http_method='GET',
            url='/endpoint',
        ),
    ]

    with pytest.warns(UserWarning) as captured_warnings:
        models = _get_models(swagger_spec)
        assert models == {
            model.get_model_name: model
            for model in expected_models
        }

    assert len(captured_warnings) == 1
    assert captured_warnings[0].message.args == (
        'Model "{}" is already defined with a different schema.\n'
        'Already known schema: {}\n'
        'New schema: {}\n'
        'Make sure that them will be named differently (via {} Swagger attributes).\n'.format(
            'model',
            sorteddict(body_schema),
            sorteddict(response_schema),
            ', '.join(SwaggerModel.SWAGGER_ATTRIBUTE_PRIORITY),

        ),
    )


def test__get_model_fields_error():
    # Reference model with no name

    _get_model_fields


def test_get_operations_to_render():
    with pytest.raises(NotImplementedError):
        get_operations_to_render(None, None)
