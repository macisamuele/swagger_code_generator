# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from argparse import Namespace

import mock
import pytest
from six import iteritems

from swagger_code_generator.main import main
from tests.conftest import BASE_PACKAGE


def _build_command_line_parameters(**kwargs):
    cli_parameters = []
    for parameter, value in iteritems(kwargs):
        if value is None:
            continue
        elif value is True:
            cli_parameters.append('--{}'.format(parameter))
        elif value is not False:
            cli_parameters.extend(['--{}'.format(parameter), value])
    return cli_parameters


def test_no_language_class_registered(mock_MetaClassRegistry):
    with pytest.raises(UserWarning) as exception_info:
        main()
        assert exception_info.value.args == ('No language classes registered to MetaClassRegistry',)


def test_help(mock_MetaClassRegistry, mock_LanguageGenerator):
    with pytest.raises(SystemExit) as exception_info:
        main('-h'.split())
    assert exception_info.value.args == (0, )

    mock_LanguageGenerator.language.assert_called_once_with()
    mock_LanguageGenerator.subparser_help.assert_called_once_with()
    mock_LanguageGenerator.set_subparser.assert_called()
    assert not mock_LanguageGenerator.validate_args.called


def test_language_help(mock_MetaClassRegistry, mock_LanguageGenerator):
    with pytest.raises(SystemExit) as exception_info:
        main('language -h'.split())
    assert exception_info.value.args == (0, )

    mock_LanguageGenerator.language.assert_called_once_with()
    mock_LanguageGenerator.subparser_help.assert_called_once_with()
    mock_LanguageGenerator.set_subparser.assert_called()
    assert not mock_LanguageGenerator.validate_args.called


@pytest.mark.parametrize(
    'swagger_path, destination_directory, operations, verbose, last_error_line',
    (
        (None, None, False, False, 'swagger is a required parameter',),
        ('/an_existing_path', None, False, False, 'destination is a required parameter',),
    )
)
@mock.patch(BASE_PACKAGE + '.main.path_or_uri_type', side_effect=lambda path: 'file://{}'.format(path))
@mock.patch(BASE_PACKAGE + '.main.path_type', side_effect=lambda path: path)
def test_check_parameters_error(
    mock_path_type, mock_path_or_uri_type, mock_MetaClassRegistry,
    mock_LanguageGenerator, swagger_path, destination_directory,
    operations, verbose, last_error_line, capsys,
):
    parameters = _build_command_line_parameters(
        swagger=swagger_path,
        destination=destination_directory,
        operations=operations,
        verbose=verbose,
    )
    with pytest.raises(SystemExit) as exception_info:
        main(parameters + [mock_LanguageGenerator.language.return_value])
    assert exception_info.value.args != (0,)
    _, error = capsys.readouterr()
    assert error.splitlines()[-1].endswith(last_error_line)
    mock_LanguageGenerator.language.assert_called_once_with()
    mock_LanguageGenerator.subparser_help.assert_called_once_with()
    mock_LanguageGenerator.set_subparser.assert_called()
    assert not mock_LanguageGenerator.validate_args.called


@pytest.mark.parametrize(
    'verbose', (True, False,),
)
@pytest.mark.parametrize(
    'operations', (True, False,),
)
@pytest.mark.parametrize(
    'swagger_path, destination_directory',
    (
        ('/an_existing_path', '/a_possible_directory',),
    )
)
@mock.patch(BASE_PACKAGE + '.main.path_or_uri_type', side_effect=lambda path: 'file://{}'.format(path))
@mock.patch(BASE_PACKAGE + '.main.path_type', side_effect=lambda path: path)
@mock.patch(BASE_PACKAGE + '.main.SwaggerClient', autospec=True)
@mock.patch(BASE_PACKAGE + '.main.configure_logger', autospec=True)
def test_check_parameters(
    mock_configure_logger, mock_SwaggerClient, mock_path_type,
    mock_path_or_uri_type, mock_MetaClassRegistry, mock_LanguageGenerator,
    swagger_path, destination_directory, operations, verbose,
):
    parameters = _build_command_line_parameters(
        swagger=swagger_path,
        destination=destination_directory,
        operations=operations,
        verbose=verbose,
    )
    main(parameters + [mock_LanguageGenerator.language.return_value])

    args = Namespace(
        destination=destination_directory,
        func=mock_LanguageGenerator.run,
        operations=operations,
        subparser=mock.ANY,
        swagger='file://{}'.format(swagger_path),
        validate=mock_LanguageGenerator.validate_args,
        verbose=verbose,
    )
    mock_LanguageGenerator.validate_args.assert_called_once_with(
        args, mock.ANY,
    )
    mock_SwaggerClient.from_url.assert_called_once_with(
        spec_url='file://{}'.format(swagger_path),
    )
    mock_LanguageGenerator.run.assert_called_once_with(
        mock_SwaggerClient.from_url.return_value.swagger_spec, args,
    )

    if verbose:
        mock_configure_logger.assert_called_once_with()
