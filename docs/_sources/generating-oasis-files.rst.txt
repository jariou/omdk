Generating Oasis Files
======================

This repository provides an executable script called
``oasis_files_generator.py`` for generating Oasis files for a given
model, supplier and model version. The resources required for the script
are as follows:

::

    1. keys data path
    2. model version file path
    3. lookup service package path
    4. canonical exposures profile path
    5. source exposures file path
    6. source exposures validation file (XSD) path
    7. source to canonical exposures file (XSLT) path
    8. canonical exposures validation file (XSD) path
    9. canonical to model exposures file (XSLT) path
    10. `xtrans.exe` CSV transformation executable path
    11. output files parent directory

The script can be executed in two ways: (1) directly by providing all
the resources in the script call using the following syntax:

::

    ./oasis_files_generator.py -k '/path/to/keys/data/folder'
                               -v '/path/to/model/version/file'
                               -l '/path/to/model/keys/lookup/service/package'
                               -p '/path/to/canonical/exposures/profile/JSON/file'
                               -e '/path/to/source/exposures/file'
                               -a '/path/to/source/exposures/validation/file'
                               -b '/path/to/source/to/canonical/exposures/transformation/file'
                               -c '/path/to/canonical/exposures/validation/file'
                               -d '/path/to/canonical/to/model/exposures/transformation/file'
                               -x '/path/to/xtrans/executable'
                               -o '/path/to/output/files/parent/directory'

or by providing the path to a JSON script config file which defines all
the script resources - the syntax for the latter option is:

::

    ./oasis_files_generator.py -f '/path/to/model/resources/JSON/config/file'

and the keys of the JSON config file should be named as follows:

::

    "keys_data_path"
    "model_version_file_path"
    "lookup_service_package_path"
    "canonical_exposures_profile_json_path"
    "source_exposures_file_path"
    "source_exposures_validation_file_path"
    "source_to_canonical_exposures_transformation_file_path"
    "canonical_exposures_validation_file_path"
    "canonical_to_model_exposures_transformation_file_path"
    "xtrans_path"
    "output_basedirpath"

The file and folder paths can be relative to the path of the script. If
you've cloned the OMDK repository then script configs for models can be
placed in the ``script_config`` subfolder, and the canonical exposures
profiles can be placed in the ``canonical_exposures_profiles``
subfolder.