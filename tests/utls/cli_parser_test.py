# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from argparse import ArgumentTypeError

import mock
import pytest
from six.moves.urllib.error import URLError

from swagger_code_generator.util.cli_parser import path_or_uri_type
from swagger_code_generator.util.cli_parser import path_type
from tests.conftest import BASE_PACKAGE


@pytest.mark.parametrize(
    'value, is_file',
    (
        ('/an_existing_path', True,),
        ('http://an.existing.url/', False,),
    )
)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.path_type', autospec=True)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.urlopen', autospec=True)
def test_path_or_uri_type_success(mock_urlopen, mock_path_type, value, is_file):
    if is_file:
        mock_path_type.return_value = value

    path_or_uri_type(value=value)

    if is_file:
        mock_path_type.assert_called_once_with(value)
        assert not mock_urlopen.called
    else:
        assert not mock_path_type.called
        mock_urlopen.assert_called_once_with(value)


@pytest.mark.parametrize(
    'value, is_file',
    (
        ('/a_not_existing_path', True,),
        ('http://a.not.existing.url/', False,),
    )
)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.path_type', autospec=True)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.urlopen', autospec=True)
def test_path_or_uri_type_error(mock_urlopen, mock_path_type, value, is_file):
    if is_file:
        mock_path_type.side_effect = ArgumentTypeError
    else:
        mock_urlopen.side_effect = URLError(mock.Mock())

    with pytest.raises(ArgumentTypeError) as exception_info:
        path_or_uri_type(value=value)

    if is_file:
        assert exception_info.value.args == ('{} is not a valid URL or PATH'.format(value), )
        mock_path_type.assert_called_once_with(value)
        assert not mock_urlopen.called
    else:
        assert exception_info.value.args == ('{} is not reachable'.format(value), )
        assert not mock_path_type.called
        mock_urlopen.assert_called_once_with(value)


@mock.patch(BASE_PACKAGE + '.util.cli_parser.abspath', autospec=True)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.expanduser', autospec=True)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.exists', autospec=True)
def test_path_type_success(mock_exists, mock_expanduser, mock_abspath):
    value = mock.Mock()
    mock_abspath.return_value = value
    mock_exists.return_value = True

    path_type(value=value)

    mock_expanduser.assert_called_once_with(value)
    mock_abspath.assert_called_once_with(mock_expanduser.return_value)
    mock_exists.assert_called_once_with(mock_abspath.return_value)


@mock.patch(BASE_PACKAGE + '.util.cli_parser.abspath', autospec=True)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.expanduser', autospec=True)
@mock.patch(BASE_PACKAGE + '.util.cli_parser.exists', autospec=True)
def test_path_type_error(mock_exists, mock_expanduser, mock_abspath):
    value = '/a_not_existing_path'
    mock_abspath.return_value = value
    mock_exists.return_value = False

    with pytest.raises(ArgumentTypeError) as exception_info:
        path_type(value=value)
    assert exception_info.value.args == ('Path \'{}\' does not exist'.format(value), )

    mock_expanduser.assert_called_once_with(value)
    mock_abspath.assert_called_once_with(mock_expanduser.return_value)
    mock_exists.assert_called_once_with(mock_abspath.return_value)
