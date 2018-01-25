#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
``generate_oasis_files.py`` is an executable script which can generate
Oasis files (items, coverages, GUL summary) for a model, given the
following arguments (in no particular order)

::

    ./generate_oasis_files.py -k /path/to/keys/data
                              -v /path/to/model/version/csv/file
                              -l /path/to/lookup/service/package
                              -p /path/to/canonical/exposures/profile/JSON/file
                              -e /path/to/source/exposures/file
                              -a /path/to/source/exposures/validation/file
                              -b /path/to/source/to/canonical/exposures/transformation/file
                              -c /path/to/canonical/exposures/validation/file
                              -d /path/to/canonical/to/model/exposures/transformation/file
                              -x /path/to/xtrans/executable
                              [-o /path/to/oasis/files/directory]

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The paths to the keys data, lookup service package, model
version file, canonical exposures profile JSON, source exposures file,
transformation and validation files, will usually be located in the
model keys server repository. The path to the Oasis files directory is
optional - by default the script will create a timestamped folder in
``omdk/runs`` with the prefix ``OasisFiles``.

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script using the path to this
file using the option ``-f`` and the (relative or absolute) path to the
file.

::

    ./generate_oasis_files.py -f /path/to/script/config/json/file

The JSON file contain the following keys (in no particular order)

::

    "keys_data_path"
    "model_version_file_path"
    "lookup_package_path"
    "canonical_exposures_profile_json_path"
    "source_exposures_file_path"
    "source_exposures_validation_file_path"
    "source_to_canonical_exposures_transformation_file_path"
    "canonical_exposures_validation_file_path"
    "canonical_to_model_exposures_transformation_file_path"
    "xtrans_path"
    "oasis_files_path"

and the values of these keys should be string paths, given relative to
the location of the JSON file. The JSON file is usually placed in the
model keys server repository. The ``"oasis_files_path"`` key is optional
- by default the script will create a timestamped folder in
``omdk/runs`` with the prefix ``OasisFiles``.
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


import argparse
import io
import json
import logging
import os
import sys
import time

from oasis_utils import (
    get_utctimestamp,
    OasisException,
)

import utils as mdk_utils
from models import OasisModelFactory as omf
from exposures import OasisExposuresManager as oem
from keys import OasisKeysLookupFactory as oklf


SCRIPT_ARGS_METADICT = {
    'config_file_path': {
        'name': 'config_file_path',
        'flag': 'f',
        'type': str,
        'help_text': 'Model config path',
        'required_on_command_line': False,
        'required_for_script': False,
        'preexists': True
    },
    'keys_data_path': {
        'name': 'keys_data_path',
        'flag': 'k',
        'type': str,
        'help_text': 'Keys data folder path for model keys lookup service',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'model_version_file_path': {
        'name': 'model_version_file_path',
        'flag': 'v',
        'type': str,
        'help_text': 'Model version file path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'lookup_package_path': {
        'name': 'lookup_package_path',
        'flag': 'l',
        'type': str,
        'help_text': 'Package path for model keys lookup service - usually in the `src/keys_server` folder of the relevant supplier repository',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'canonical_exposures_profile_json_path': {
        'name': 'canonical_exposures_profile_json_path',
        'flag': 'p',
        'type': str,
        'help_text': 'Path of the supplier canonical exposures profile JSON file',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'source_exposures_file_path': {
        'name': 'source_exposures_file_path',
        'flag': 'e',
        'type': str,
        'help_text': 'Source exposures file path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'source_exposures_validation_file_path': {
        'name': 'source_exposures_validation_file_path',
        'flag': 'a',
        'type': str,
        'help_text': 'Source exposures validation file (XSD) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'source_to_canonical_exposures_transformation_file_path': {
        'name': 'source_to_canonical_exposures_transformation_file_path',
        'flag': 'b',
        'type': str,
        'help_text': 'Source -> canonical exposures transformation file (XSLT) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'canonical_exposures_validation_file_path': {
        'name': 'canonical_exposures_validation_file_path',
        'flag': 'c',
        'type': str,
        'help_text': 'Canonical exposures validation file (XSD) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'canonical_to_model_exposures_transformation_file_path': {
        'name': 'canonical_to_model_exposures_transformation_file_path',
        'flag': 'd',
        'type': str,
        'help_text': 'Canonical -> model exposures transformation file (XSLT) path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'xtrans_path': {
        'name': 'xtrans_path',
        'flag': 'x',
        'type': str,
        'help_text': 'Path of the xtrans executable which performs the source -> canonical and canonical -> model exposures transformations',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'oasis_files_path': {
        'name': 'oasis_files_path',
        'flag': 'o',
        'type': str,
        'help_text': 'Directory to place generated Oasis files for the model',
        'required_on_command_line': False,
        'required_for_script': False,
        'preexists': False
    }
}


if __name__ == '__main__':

    logger = mdk_utils.set_logging()
    logger.info('Console logging set')

    try:
        logger.info('Parsing script arguments')
        args = mdk_utils.parse_script_args(SCRIPT_ARGS_METADICT, desc='Generate Oasis files for a model')

        if args['config_file_path']:
            logger.info('Loading script arguments from config file {}'.format(args['config_file_path']))
            args = mdk_utils.load_script_args_from_config_file(SCRIPT_ARGS_METADICT, args['config_file_path'])
        else:
            args.pop('config_file_path')

        logger.info('Script arguments: {}'.format(json.dumps(args, indent=4, sort_keys=True)))

        di = SCRIPT_ARGS_METADICT
        missing = filter(lambda arg: not args[arg] if arg in args and di[arg]['required_for_script'] else None, di)

        if missing:
            raise OasisException('Not all script resources arguments provided - missing {}'.format(missing))

        logger.info('Getting model info and creating lookup service instance')
        model_info, model_klc = oklf.create(
            model_keys_data_path=args['keys_data_path'],
            model_version_file_path=args['model_version_file_path'],
            lookup_package_path=args['lookup_package_path']
        )
        time.sleep(3)
        logger.info('\t{}, {}'.format(model_info, model_klc))

        args['lookup'] = model_klc

        logger.info('Creating Oasis model object')
        model = omf.create(
            model_supplier_id=model_info['supplier_id'],
            model_id=model_info['model_id'],
            model_version_id=model_info['model_version_id']
        )
        logger.info('Created Oasis model object {}'.format(model))

        utcnow = get_utctimestamp(fmt='%Y%m%d%H%M%S')

        logger.info('Checking for Oasis files path')
        try:
            if 'oasis_files_path' not in args or not args['oasis_files_path']:
                args['oasis_files_path'] = os.path.join(os.getcwd(), 'runs', 'OasisFiles-{}'.format(utcnow))
                logger.info('Oasis files path not provided - creating one in omdk/runs')
                os.mkdir(args['oasis_files_path'])
            else:
                if not os.path.exists(args['oasis_files_path']):
                    logger.info('Oasis files path {} does not exist - creating one'.format(args['oasis_files_path']))
                    os.mkdir(args['oasis_files_path'])
                
        except (IOError, OSError) as e:
            raise OasisException('Error processing or creating Oasis files path: {}'.format(str(e)))

        logger.info('Oasis files path {} set up for model {}'.format(args['oasis_files_path'], model.key))

        logger.info('Creating an Oasis exposures manager for model')
        manager = oem(oasis_models=[model])
        logger.info('\t{}'.format(manager))

        logger.info('Generating Oasis files for model')
        oasis_files = manager.start_files_pipeline(model, with_model_resources=False, **args)

        logger.info('Generated Oasis files for model: {}'.format(oasis_files))
    except OasisException as e:
        logger.error(str(e))
        sys.exit(-1)

    sys.exit(0)
