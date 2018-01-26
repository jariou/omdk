#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
``generate_keys.py`` is an executable script which can generate and
write Oasis keys (area peril ID, vulnerability ID) for a model, given
the following arguments (in no particular order)

::

    ./generate_keys.py -k /path/to/keys/data
                       -v /path/to/model/version/csv/file
                       -l /path/to/lookup/service/package
                       -e /path/to/model/exposures/csv/file
                       -o /path/to/output/file
                       [-f <output format - 'oasis_keys' or 'list_keys'>]

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The paths to the keys data, lookup service package (Python
package containing the lookup source code), and model version file will
usually be located in the model keys server (Git) repository. If the
repository was created by or is managed by Oasis LMF then the lookup
service package will usually be contained in the ``src/keys_server``
Python subpackage and can be given as the path to that subpackage (see
the OasisPiWind repository as a reference for how to structure an Oasis
keys server repository)

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script with option ``-f`` and
the (relative or absolute) path to the file.

::

    ./generate_keys.py -f /path/to/script/config/json/file

The JSON file should contain the following keys (in no particular order)

::

    "keys_data_path"
    "model_version_file_path"
    "lookup_package_path"
    "model_exposures_file_path"
    "output_file_path"
    "output_format"

and the values of the path-related keys should be string paths, given
relative to the location of JSON file. The JSON file is usually placed
in the model keys server repository. The ``"output_format"`` key is
optional - by default the script will generate an Oasis keys file.

Keys records returned by an Oasis keys lookup service (see the PiWind
lookup service for reference) will be Python dicts with the following
structure

::

    {
        "id": <loc. ID>,
        "peril_id": <Oasis peril type ID - oasis_utils/oasis_utils.py>,
        "coverage": <Oasis coverage type ID - see oasis_utils/oasis_utils.py>,
        "area_peril_id": <area peril ID>,
        "vulnerability_id": <vulnerability ID>,
        "message": <lookup status message>,
        "status": <lookup status code - see oasis_utils/oasis_utils.py>
    }

The ``generate_keys.py`` script can generate keys records in this
format, and write them to file.

For model loss calculations however ktools requires a keys CSV file with
the following format

::

    LocID,PerilID,CoverageID,AreaPerilID,VulnerabilityID
    ..
    ..

where the headers correspond to the relevant Oasis keys record fields. The ``generate_keys.py`` script can also generate and
write Oasis keys files. 
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
import logging
import os
import sys

from oasis_utils import OasisException

from keys import OasisKeysLookupFactory

import utils as mdk_utils


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
        'help_text': 'Keys data folder path',
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
        'help_text': 'Path of the lookup service package - in the supplier repository this is usually the `src/keys_server` folder',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'model_exposures_file_path': {
        'name': 'model_exposures_file_path',
        'flag': 'e',
        'type': str,
        'help_text': 'Model exposures file path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': True
    },
    'output_file_path': {
        'name': 'output_file_path',
        'flag': 'o',
        'type': str,
        'help_text': 'Keys records output file path',
        'required_on_command_line': False,
        'required_for_script': True,
        'preexists': False
    },
    'output_format': {
        'name': 'output_format',
        'flag': 't',
        'type': str,
        'help_text': 'Keys records file output format: choices are `oasis_keys` and `list_keys`',
        'required_on_command_line': False,
        'required_for_script': False
    }
}


if __name__ == '__main__':

    logger = mdk_utils.set_logging()
    logger.info('Console logging set')

    try:
        logging.info('Parsing script arguments')
        args = mdk_utils.parse_script_args(SCRIPT_ARGS_METADICT, desc='Generate Oasis keys file for a model')
        
        if args['config_file_path']:
            logger.info('Loading script resources from config file {}'.format(args['config_file_path']))
            args = mdk_utils.load_script_args_from_config_file(SCRIPT_ARGS_METADICT, args['config_file_path'])
        else:
            args.pop('config_file_path')

        logger.info('Script arguments: {}'.format(args))

        di = SCRIPT_ARGS_METADICT
        missing = filter(lambda arg: not args[arg] if arg in args and di[arg]['required_for_script'] else None, di)

        if missing:
            raise OasisException('Not all script resources arguments provided - missing {}'.format(missing))

        logging.info('Creating Oasis keys lookup factory')
        oklf = OasisKeysLookupFactory()
        logging.info('{}'.format(oklf))

        logging.info('Getting model info and creating lookup service instance')
        model_info, model_klc = oklf.create(
            model_keys_data_path=args['keys_data_path'],
            model_version_file_path=args['model_version_file_path'],
            lookup_package_path=args['lookup_package_path']
        )
        logging.info('Loaded model info {}'.format(json.dumps(model_info, indent=4, sort_keys=True)))
        logging.info('Loaded model lookup service {}'.format(model_klc))

        output_format = (
            args['output_format'] if 'output_format' in args and args['output_format']
            else 'oasis_keys'
        )
        logging.info('Saving keys records to file')
        f, n = oklf.save_keys(
            lookup=model_klc,
            model_exposures_file_path=args['model_exposures_file_path'],
            output_file_path=args['output_file_path'],
            format=output_format
        )
    except OasisException as e:
        logging.error(str(e))
        sys.exit(-1)

    logging.info('{} keys records saved to file {}'.format(n, f))
    sys.exit(0)
