#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MDK internal utilities
"""

from __future__ import print_function

__all__ = [
    'load_script_args_from_config_file',
    'parse_script_args',
    'set_logging'
]

import argparse
import io
import json
import logging
import os

from oasis_utils import OasisException


def load_script_args_from_config_file(script_args_metadict, config_file_path):
    """
    Returns a script arguments dict from a JSON config file.
    """
    di = script_args_metadict

    if config_file_path.endswith('json'):
        try:
            with io.open(config_file_path, 'r', encoding='utf-8') as f:
                args = json.load(f)
        except (IOError, TypeError, ValueError) as e:
            raise OasisException('Error parsing script resources config file {}: {}'.format(config_file_path, str(e)))

        try:
            parent_dir = os.path.abspath(os.pardir)
            map(
                lambda arg: args.update({arg: os.path.join(parent_dir, args[arg])}) if arg.endswith('path') and args[arg] else None,
                args
            )

            invalid_paths = dict(
                (path_key, args[path_key]) for path_key in
                filter(lambda arg: arg in di and arg.endswith('path') and di[arg]['preexists'] and args[arg] and not os.path.exists(args[arg]), args)
            )
            if invalid_paths:
                raise OasisException('Error parsing script resources config file: paths {} are invalid'.format(invalid_paths))
        except OSError as e:
            raise OasisException('Error parsing script resources config file: {}'.format(str(e)))
    elif config_file_path.endswith('yaml') or config_file_path.endswith('yml'):
        raise OasisException('Error parsing script resources config file: YAML file not supported')

    return args


def parse_script_args(script_args_metadict, desc=None):
    """
    Parses script arguments using a script arguments meta dict, constructs and
    returns an args dictionary.
    """
    parser = argparse.ArgumentParser(description=desc)

    di = script_args_metadict

    try:
        non_bools = filter(lambda arg: di[arg]['type'] != bool, di)
        map(
            lambda arg: parser.add_argument(
                '--{}'.format(di[arg]['name']),
                '-{}'.format(di[arg]['flag']),
                type=di[arg]['type'],
                required=di[arg]['required_on_command_line'],
                help=di[arg]['help_text']
            ),
            non_bools
        )

        bools = filter(lambda arg: arg not in non_bools, di)
        map(
            lambda arg: (
                parser.add_argument(
                    '--{}'.format(di[arg]['name']),
                    dest=di[arg]['dest'],
                    action='store_true',
                    default=(True if di[arg]['default'] else False),
                    help=di[arg]['help_text']
                ),
                parser.add_argument(
                    '--no-{}'.format(di[arg]['name']),
                    dest=di[arg]['dest'],
                    action='store_false',
                    help=di[arg]['help_text']
                ),
            ),
            bools
        )

        args = vars(parser.parse_args())

        map(
            lambda arg: args.update({arg: os.path.abspath(args[arg])}) if arg.endswith('path') and args[arg] else None,
            args
        )

        invalid_paths = dict(
            (path_key, args[path_key]) for path_key in
            filter(lambda arg: arg in di and arg.endswith('path') and di[arg]['preexists'] and args[arg] and not os.path.exists(args[arg]), args)
        )
        if invalid_paths:
            raise OasisException('Error parsing script args: paths {} are invalid'.format(invalid_paths))
    except (KeyError, argparse.ArgumentError, argparse.ArgumentTypeError, OSError) as e:
        raise OasisException(e)

    return args


def set_logging(
    level=logging.INFO,
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    filename=None,
    filemode='w',
    stream=None
):
    """
    Sets up and returns a logger.
    """
    try:
        logging.basicConfig(
            level=level,
            format=fmt,
            filename=filename,
            filemode='w',
            stream=stream
        )
    except (OSError, IOError) as e:
        raise OasisException(e)

    return logging.getLogger()
