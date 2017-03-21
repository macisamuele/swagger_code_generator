# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta

from six import add_metaclass

from swagger_code_generator.util.datastructure import abstractclassmethod
from swagger_code_generator.util.datastructure import frozendict
from swagger_code_generator.util.swagger import get_models_to_render
from swagger_code_generator.util.swagger import get_operations_to_render


class MetaClassRegistry(ABCMeta):
    __REGISTRY = {}

    def __new__(mcs, cls_name, bases, attributes):
        metaclass_attribute_name = '__{attribute}'.format(
            attribute=mcs.__name__,
        )
        if metaclass_attribute_name not in attributes:
            attributes[metaclass_attribute_name] = None

        cls = super(MetaClassRegistry, mcs).__new__(
            mcs,
            cls_name,
            bases,
            attributes,
        )

        # Register class
        if attributes[metaclass_attribute_name] is None:
            key = '{Module}.{Class}'.format(
                Module=cls.__module__,
                Class=cls.__name__,
            )
            if key not in mcs.__REGISTRY:
                mcs.__REGISTRY[key] = cls
        return cls

    @classmethod
    def registry(mcs):
        return frozendict(mcs.__REGISTRY)

    @classmethod
    def registry_keys(mcs):
        return frozenset(mcs.__REGISTRY.keys())

    @classmethod
    def registry_classes(mcs):
        return frozenset(mcs.__REGISTRY.values())


@add_metaclass(ABCMeta)
class AbstractLanguageGenerator(object):

    @classmethod
    def subparser_help(cls):
        pass

    @abstractclassmethod
    def language(cls):
        pass

    @abstractclassmethod
    def set_subparser(cls, subparser):
        pass

    @abstractclassmethod
    def validate_args(cls, args, error_method):
        pass

    @abstractclassmethod
    def render(cls, swagger_spec, models_to_render, operations_to_render, args=()):
        pass

    @classmethod
    def run(cls, swagger_spec, args=()):
        models_to_render = get_models_to_render(swagger_spec)
        operations_to_render = get_operations_to_render(
            swagger_spec, models_to_render
        ) if args.operations else ()

        cls.render(
            swagger_spec=swagger_spec,
            models_to_render=models_to_render,
            operations_to_render=operations_to_render,
            args=args,
        )
