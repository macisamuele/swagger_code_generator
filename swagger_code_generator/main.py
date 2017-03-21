# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys
from argparse import ArgumentParser
from warnings import simplefilter
from warnings import warn

from bravado.client import SwaggerClient
from cookiecutter.log import configure_logger
from six import iteritems

from swagger_code_generator.generator_metaclass import MetaClassRegistry
from swagger_code_generator.util.cli_parser import path_or_uri_type
from swagger_code_generator.util.cli_parser import path_type


def main(argv=()):
    simplefilter('error')   # Ensure that in case if warning the tool execution is interrupted

    cli_parser = ArgumentParser('Swagger Models Class Generator')

    cli_parser.add_argument(
        '-s', '--swagger',
        type=path_or_uri_type,
        help='Root Swagger Spec URI (ie: file://.., http[s]://.., etc.)',
    )

    cli_parser.add_argument(
        '-d', '--destination',
        type=path_type,
        help='Destination directory of the generated files',
    )
    cli_parser.add_argument(
        '-o', '--operations',
        action='store_true',
        help='Generate Operations Handling',
    )
    cli_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose Logging',
    )

    if not MetaClassRegistry.registry_classes():
        warn('No language classes registered to {}'.format(MetaClassRegistry))

    subparsers = cli_parser.add_subparsers(help='Language to generate')
    for registry_class in MetaClassRegistry.registry_classes():
        subparser = subparsers.add_parser(
            registry_class.language(),
            **{k: v for k, v in iteritems({'help': registry_class.subparser_help()}) if v}
        )
        subparser.set_defaults(func=registry_class.run, validate=registry_class.validate_args, subparser=subparser)
        registry_class.set_subparser(subparser)

    args = cli_parser.parse_args(argv)

    if not args.swagger:
        cli_parser.error('swagger is a required parameter')

    if not args.destination:
        cli_parser.error('destination is a required parameter')

    args.validate(args, args.subparser.error)

    swagger_client = SwaggerClient.from_url(spec_url=args.swagger)

    if args.verbose:
        configure_logger()

    args.func(swagger_client.swagger_spec, args)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
