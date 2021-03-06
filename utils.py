# -*- coding: utf-8 -*-

"""
MDK internal utilities
"""

# BSD 3-Clause License
# 
# Copyright (c) 2017-2020, Oasis Loss Modelling Framework
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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

    cfp = config_file_path if os.path.isabs(config_file_path) else os.path.abspath(config_file_path)
    cfd = os.path.dirname(cfp)

    if cfp.endswith('json'):
        try:
            with io.open(cfp, 'r', encoding='utf-8') as f:
                args = json.load(f)
        except (IOError, TypeError, ValueError) as e:
            raise OasisException('Error parsing script resources config file {}: {}'.format(cfp, str(e)))

        try:
            map(
                lambda arg: args.update({arg: os.path.join(cfd, args[arg])}) if arg.endswith('path') and args[arg] else None,
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
    elif cfp.endswith('yaml') or cfp.endswith('yml'):
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
