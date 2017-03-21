# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import namedtuple
from itertools import chain
from re import sub
from warnings import warn

from bravado_core.schema import collapsed_properties
from bravado_core.schema import get_format
from bravado_core.schema import is_prop_nullable
from bravado_core.spec import strip_xscope
from inflection import camelize
from six import iteritems
from six import itervalues
from swagger_spec_validator.validator20 import get_collapsed_properties_type_mappings

from swagger_code_generator.util.datastructure import sorteddict

SwaggerField = namedtuple('SwaggerField', ['required', 'nullable', 'type', 'format', 'is_primitive', 'schema'])


def _strip_unwanted_characters_from_url(url):
    return sub('[/{}]', '_', url)


class SwaggerModel(object):
    SWAGGER_ATTRIBUTE_PRIORITY = ['x-title', 'x-model', 'title']

    def __init__(self, schema):
        self.schema = schema
        self.fields = {}

    @property
    def get_model_name(self):
        for field in self.SWAGGER_ATTRIBUTE_PRIORITY:
            if field in self.schema:
                return self.schema[field]
        else:
            return self.get_model_name_fallback()

    def get_model_name_fallback(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return isinstance(other, self.__class__.__bases__) and \
            self.get_model_name == other.get_model_name and \
            self.schema == other.schema


class SwaggerBodyModel(SwaggerModel):
    def __init__(self, schema, http_method, url):
        super(SwaggerBodyModel, self).__init__(schema)
        self.http_method = http_method
        self.url = url

    def __hash__(self):
        return hash((self.http_method, self.url))

    def get_model_name_fallback(self):
        return camelize('{}{}'.format(self.http_method, _strip_unwanted_characters_from_url(self.url)))


class SwaggerResponseModel(SwaggerModel):
    def __init__(self, schema, http_method, response_code, url):
        super(SwaggerResponseModel, self).__init__(schema)
        self.http_method = http_method
        self.response_code = response_code
        self.url = url

    def __hash__(self):
        return hash((self.http_method, self.response_code, self.url))

    def get_model_name_fallback(self):
        return camelize(
            '{}{}{}'.format(self.http_method, self.response_code, _strip_unwanted_characters_from_url(self.url))
        )


def _get_models(swagger_spec):
    deref = swagger_spec.deref
    all_models = {}
    seen_models = set()

    body_models = {
        SwaggerBodyModel(model, operation.http_method.upper(), operation.path_name)
        for resource in itervalues(swagger_spec.resources)
        for operation in itervalues(resource.operations)
        if 'body' in operation.params
        for model in [deref(operation.params['body'].param_spec['schema'])]
    }

    response_models = {
        SwaggerResponseModel(model, operation.http_method.upper(), response_code, operation.path_name)
        for resource in itervalues(swagger_spec.resources)
        for operation in itervalues(resource.operations)
        for response_code in operation.op_spec['responses']
        if 'schema' in operation.op_spec['responses'][response_code]
        for model in [deref(operation.op_spec['responses'][response_code]['schema'])]
    }

    for swagger_model in chain(body_models, response_models):
        model_name = swagger_model.get_model_name
        if model_name not in seen_models:
            seen_models.add(model_name)
            all_models[model_name] = swagger_model
        elif strip_xscope(all_models[model_name].schema) != strip_xscope(swagger_model.schema):
            warn(
                'Model "{}" is already defined with a different schema.\n'
                'Already known schema: {}\n'
                'New schema: {}\n'
                'Make sure that them will be named differently (via {} Swagger attributes).\n'.format(
                    model_name,
                    sorteddict(strip_xscope(all_models[model_name].schema)),
                    sorteddict(strip_xscope(swagger_model.schema)),
                    ', '.join(SwaggerModel.SWAGGER_ATTRIBUTE_PRIORITY),
                )
            )

    return all_models


def _get_model_fields(swagger_spec, schema, known_models):
    deref = swagger_spec.deref
    required_properties, not_required_properties = get_collapsed_properties_type_mappings(
        definition=schema,
        deref=deref,
    )

    fields = {}

    for prop_name, prop_schema in iteritems(collapsed_properties(schema, swagger_spec)):
        is_required = prop_name in required_properties
        is_primitive = True
        if is_required:
            prop_type = required_properties[prop_name]
        else:
            prop_type = not_required_properties[prop_name]
        # Check for references!!! if $ref: #/definitions/Model then type is Model
        if prop_type == 'object':
            swagger_model = SwaggerModel(deref(prop_schema))
            prop_type = swagger_model.get_model_name
            if prop_type is None:
                warn(
                    'Schema {} references a model with no name.\n'
                    'Please assign a name to model with one of {} Swagger attribute.\n'
                    'Property: {}, Schema: {}'.format(
                        schema,
                        SwaggerModel.SWAGGER_ATTRIBUTE_PRIORITY,
                        prop_name,
                        sorteddict(prop_schema),
                    )
                )
            elif prop_type not in known_models:
                known_models[prop_type] = swagger_model
            is_primitive = False
        elif prop_type == 'array':
            inner_schema = deref(prop_schema['items'])
            inner_type = inner_schema.get('type')
            is_inner_primitive = True
            if not inner_type or inner_type == 'object':
                inner_type = SwaggerModel(inner_schema).get_model_name
                if inner_type is None:
                    warn(
                        'Schema {} references a model with no name.\n'
                        'Please assign a name to model with one of {} Swagger attribute.\n'
                        'Property: {}, Schema: {}'.format(
                            schema,
                            SwaggerModel.SWAGGER_ATTRIBUTE_PRIORITY,
                            sorteddict(inner_schema),
                            sorteddict(inner_type),
                        )
                    )
                is_inner_primitive = False
            prop_type = SwaggerField(
                required=True,
                nullable=False,
                is_primitive=is_inner_primitive,
                type=inner_type,
                format=None,
                schema=prop_schema,
            )

        fields[prop_name] = SwaggerField(
            required=is_required,
            nullable=is_prop_nullable(swagger_spec, prop_schema),
            is_primitive=is_primitive,
            type=prop_type,
            format=get_format(swagger_spec, prop_schema),   # TOOD: understand how to handle enums
            schema=prop_schema
        )

    return fields


def get_models_to_render(swagger_spec):
    body_and_response_models = _get_models(swagger_spec)

    iterate_again = True

    rendered = set()

    while iterate_again:
        starting_model_names = set(body_and_response_models)
        for model_name in starting_model_names:
            if model_name not in rendered:
                body_and_response_models[model_name].fields = _get_model_fields(
                    swagger_spec=swagger_spec,
                    schema=body_and_response_models[model_name].schema,
                    known_models=body_and_response_models,
                )
                rendered.add(model_name)
        iterate_again = len(starting_model_names) != len(body_and_response_models)

    return body_and_response_models


def get_operations_to_render(swagger_spec, known_models):
    raise NotImplementedError()
