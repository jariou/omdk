Building and running models
===========================

The repository provides a Python toolkit for building, running and
testing Oasis models end-to-end, including performing individual steps
in this process. It includes:

-  a Python class framework for working with Oasis models and model
   resources as Python objects (the ``models`` subpackage)
-  a Python class framework for managing model exposures and resources,
   and also for generating Oasis files from these (the ``exposures``
   subpackage)
-  a Python factory class for instantiating keys lookup services for
   models, and generating and saving keys outputs from these lookup
   services (the ``keys`` subpackage)
-  executable scripts, based on these class frameworks, for writing keys
   outputs from model lookup services (``generate_keys.py``), generating
   Oasis files from model source exposures and other resources
   (``generate_oasis_files.py``), and generating losses for models
   (``generate_losses.py``). This includes a "master" script that can
   perform all these steps to run the model end-to-end
   (``run_model.py``).

Generating keys
---------------

``generate_keys.py`` is an executable script which can generate and
write Oasis keys (area peril ID, vulnerability ID) for a model, given
the following arguments (in no particular order)

::

    ./generate_keys.py -k /path/to/keys/data
                       -v /path/to/model/version/csv/file
                       -l /path/to/lookup/service/package
                       -e /path/to/model/exposures/csv/file
                       -o /path/to/output/file
                       -f <output format - 'oasis_keys' or 'list_keys'>

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The paths to the keys data, lookup service package (Python
package containing the lookup source code), and model version file will
usually be located in the model keys server (Git) repository. If the
repository was created by or is managed by Oasis LMF then the lookup
service package will usually be contained in the ``src/keys_server``
Python subpackage and can be given as the path to that subpackage (see
the `OasisPiWind <https://github.com/OasisLMF/OasisPiWind>`_ repository
as a reference for how to structure an Oasis keys server repository).

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script with option ``-f`` and
the path to the file. In this case the paths should be given relative to
the parent folder in which the model keys server repository is located.

::

    ./generate_keys.py -f /path/to/keys/script/config/file

The JSON file should contain the following keys (in no particular order)

::

    "keys_data_path"
    "model_version_file_path"
    "lookup_package_path"
    "model_exposures_file_path"
    "output_file_path"
    "output_format"

and the values of these keys should be string paths, given relative to
the parent folder in which the model keys server repository is located.
The JSON file is usually placed in the model keys server repository.

Keys records returned by an Oasis keys lookup service (see the `PiWind lookup service <https://github.com/OasisLMF/OasisPiWind/blob/master/src/keys_server/PiWindKeysLookup.py>`_
for reference) will be Python dicts with the following structure

::

    {
        "id": <loc. ID>,
        "peril_id": <Oasis peril type ID - see oasis_utils/oasis_utils.py>,
        "coverage": <coverage type ID - see oasis_utils/oasis_utils.py>,
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

where the headers correspond to the relevant Oasis keys record fields.
The ``generate_keys.py`` script can also generate and write Oasis keys files.

Generating Oasis files
----------------------

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
                              -o /path/to/oasis/files/directory

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The paths to the keys data, lookup service package, model
version file, canonical exposures profile JSON, source exposures file,
transformation and validation files, will usually be located in the
model keys server repository.

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script using the path to this
file using the option ``-f``. In this case the paths should be given
relative to the parent folder in which the model keys server repository
is located.

::

    ./generate_oasis_files.py -f /path/to/model/resources/JSON/config/file

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
the parent folder in which the model keys server repository is located.
The JSON file is usually placed in the model keys server repository.

Generating losses
-----------------

``generate_losses.py`` is an executable script which, given a model
analysis settings JSON file, model data and some other parameters, can
generate a (Bash) shell script containing ktools commands to calculate
losses, and also execute the generated script to generate those outputs
using the installed ktools framework. The script can be called directly
from the command line given the following arguments (in no particular
order)

::

    ./generate_losses.py -j /path/to/analysis/settings/json/file
                         -s <ktools script name (without file extension)>
                         -m /path/to/model/data
                         -r /path/to/model/run/directory
                         -n <number of ktools calculation processes to use>
                         [--execute | --no-execute]

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The ktools script name should not contain any filetype
extension, and the model run directory can be placed anywhere in the
parent folder common to ``omdk`` and the model keys server repository.

The model run directory must contain the analysis settings JSON file and
either the actual model data or at least symlinked model data files (in
the ``static`` subfolder). It must have the following folder structure

::

    ├── analysis_settings.json
    ├── fifo/
    ├── input/
    ├── output/
    ├── static/
    └── work/

The losses are written in the ``output`` subfolder as CSV files.

By default executing ``generate_losses.py`` will automatically execute
the ktools losses script it generates. If you don't want this provide
the (optional) ``--no-execute`` argument. The default here is automatic
execution.

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script using the path to this
file using the option ``-f``. In this case the paths should be given
relative to the parent folder in which the model keys server repository
is located.

::

    ./generate_losses.py -f /path/to/model/resources/JSON/config/file'

The JSON file should contain the following keys (in no particular order)

::

    "analysis_settings_json_file_path"
    "ktools_script_name"
    "model_data_path"
    "model_run_dir_path"
    "ktools_num_processes"
    "execute"

and the values of the path-related keys should be string paths, given
relative to the parent folder in which the model keys server repository
is located. The JSON file is usually placed in the model keys server
repository. The value of the (optional) ``"exectute"`` key should be
either ``true`` or ``false`` depending on whether you want the generated
ktools losses scripts to be automatically executed or not. The default
here is automatic execution.

Running a model end-to-end
--------------------------

``run_model.py`` is an executable "master" script that can run models
end-to-end, i.e. generate losses given model resources, including keys
data, canonical exposure profiles, exposure transformation and
validation files, model data, analysis settings etc., given the
following arguments (in no particular order)

::

    ./run_model.py -k /path/to/keys/data/folder
                   -v /path/to/model/version/file
                   -l /path/to/model/keys/lookup/service/package
                   -p /path/to/canonical/exposures/profile/JSON/file
                   -e /path/to/source/exposures/file
                   -a /path/to/source/exposures/validation/file
                   -b /path/to/source/to/canonical/exposures/transformation/file
                   -c /path/to/canonical/exposures/validation/file
                   -d /path/to/canonical/to/model/exposures/transformation/file
                   -x /path/to/xtrans/executable
                   -j /path/to/analysis/settings/json/file
                   -s <ktools script name (without file extension)>
                   -m /path/to/model/data
                   -r /path/to/model/run/directory
                   -n <number of ktools calculation processes to use>

When calling the script this way paths can be given relative to the
script, in particular, file paths should include the filename and
extension. The paths to the keys data, lookup service package, model
version file, canonical exposures profile JSON, source exposures file,
transformation and validation files, and analysis settings JSON file,
will usually be located in the model keys server repository. The ktools
script name should not contain any filetype extension, and the model run
directory can be placed anywhere in the parent folder common to ``omdk``
and the model keys server repository.

It is also possible to run the script by defining these arguments in a
JSON configuration file and calling the script using the path to this
file using the option ``-f``. In this case the paths should be given
relative to the parent folder in which the model keys server repository
is located.

::

    ./run_model.py -f /path/to/model/resources/JSON/config/file'

The JSON file should contain the following keys (in no particular order)

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
    "analysis_settings_json_file_path"
    "ktools_script_name"
    "model_data_path"
    "model_run_dir_path"
    "ktools_num_processes"

and the values of the path-related keys should be string paths, given
relative to the parent folder in which the model keys server repository
is located. The JSON file is usually placed in the model keys server
repository.

**NOTE**: For a given model the JSON script configuration files for
``generate_oasis_files.py``, ``generate_losses.py`` and ``run_model.py``
should complement each other, so you can run any of these scripts
against a single master script configuration file.

As an example, this is the master script configuration file for PiWind

::

    {
        "model_data_path": "OasisPiWind/model_data/PiWind",
        "keys_data_path": "OasisPiWind/keys_data/PiWind",
        "model_version_file_path": "OasisPiWind/keys_data/PiWind/ModelVersion.csv", 
        "lookup_package_path": "OasisPiWind/src/keys_server",
        "canonical_exposures_profile_json_path": "OasisPiWind/oasislmf-piwind-canonical-profile.json",
        "source_exposures_file_path": "OasisPiWind/tests/data/SourceLocPiWind.csv",
        "source_exposures_validation_file_path": "OasisPiWind/flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_SourceLoc.xsd",
        "source_to_canonical_exposures_transformation_file_path": "OasisPiWind/flamingo/PiWind/Files/TransformationFiles/MappingMapToGeneric_Windstorm_CanLoc_A.xslt",
        "canonical_exposures_validation_file_path": "OasisPiWind/flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_CanLoc_B.xsd",
        "canonical_to_model_exposures_transformation_file_path": "OasisPiWind/flamingo/PiWind/Files/TransformationFiles/MappingMapTopiwind_modelloc.xslt",
        "xtrans_path": "omdk/xtrans/xtrans.exe",
        "oasis_files_path": "omdk/tests/data/oasislmf-piwind-0.0.0.1",
        "model_run_dir_path": "omdk/tests/data/oasislmf-piwind-0.0.0.1",
        "analysis_settings_json_file_path": "OasisPiWind/analysis_settings.json",
        "ktools_script_name": "run_ktools",
        "ktools_num_processes": 2
    }

It can also be obtained from `https://github.com/OasisLMF/OasisPiWind/blob/master/mdk-oasislmf-piwind.json <https://github.com/OasisLMF/OasisPiWind/blob/master/mdk-oasislmf-piwind.json>`_.