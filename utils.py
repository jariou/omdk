#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MDK internal utilities
"""

__all__ = [
    'parse_script_args',
    'set_logging',
    'load_script_args_from_config_file'

]

import argparse
import io
import json
import logging
import os

from oasis_utils import OasisException


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
    except Exception as e:
        raise OasisException(e)

    return logging.getLogger()


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
                required=di[arg]['required'],
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
    except Exception as e:
        raise OasisException(e)

    return args


def load_script_args_from_config_file(config_file_path):
    """
    Returns a script arguments dict from a JSON config file.
    """
    try:
        if config_file_path.endswith('json'):
            try:
                with io.open(config_file_path, 'r', encoding='utf-8') as f:
                    args = json.load(f)
            except (IOError, TypeError, ValueError) as e:
                raise OasisException('Error parsing resources config file {}: {}'.format(config_file_path, str(e)))

            parent_dir = os.path.abspath(os.pardir)
            map(
                lambda arg: args.update({arg: os.path.join(parent_dir, args[arg])}) if arg.endswith('path') and args[arg] else None,
                args
            )
        elif config_file_path.endswith('yaml') or config_file_path.endswith('yml'):
            pass
    except Exception as e:
        raise OasisException(e)

    return args
