# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from os import sep as path_separator
from os.path import abspath
from os.path import dirname
from os.path import join

from cookiecutter.generate import generate_files
from cookiecutter.log import configure_logger
from six import add_metaclass
from six import iteritems

from swagger_code_generator.generator_metaclass import AbstractLanguageGenerator
from swagger_code_generator.generator_metaclass import MetaClassRegistry


@add_metaclass(MetaClassRegistry)
class JavaGenerator(AbstractLanguageGenerator):

    def __init__(self):
        pass

    @classmethod
    def subparser_help(cls):
        return 'Java Swagger Handling'

    @classmethod
    def language(cls):
        return 'java'

    @classmethod
    def set_subparser(cls, subparser):
        subparser.add_argument('-p', '--package', help='Java Package')
        subparser.add_argument('-sr', '--src-root', help='Source code root directory (relative path from destination)')
        subparser.add_argument('-tr', '--test-root', help='Test code root directory (relative path from destination)')

    @classmethod
    def validate_args(cls, args, error_method):
        if not args.package:
            error_method('package is a required parameter')
        if not args.src_root:
            error_method('src-root is a required parameter')
        if not args.test_root:
            error_method('test-root is a required parameter')

    @classmethod
    def render(cls, swagger_spec, models_to_render, operations_to_render, args=()):
        if args.verbose:
            configure_logger()

        for model, swagger_model in iteritems(models_to_render):
            print(model)

        cookiecutter_context = {
            'cookiecutter': {
                'java_package': args.package,
                'java_package_dir': args.package.replace('.', path_separator),
                'java_source_root': args.src_root,
                'java_test_root': args.test_root,
            },
        }

        generate_files(
            repo_dir=join(dirname(abspath(__file__)), 'src',),
            context=cookiecutter_context,
            overwrite_if_exists=True,
            output_dir=args.destination,
        )
        generate_files(
            repo_dir=join(dirname(abspath(__file__)), 'test',),
            context=cookiecutter_context,
            overwrite_if_exists=True,
            output_dir=args.destination,
        )
