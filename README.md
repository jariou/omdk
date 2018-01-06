Oasis Model Development Kit (OMDK)
==================================

OMDK provides a Python framework and utilities for building, developing, running and testing Oasis models.

# Repository Management

## Cloning the repository

You can clone this repository from <a href="https://github.com/OasisLMF/omdk" target="_blank">GitHub</a> using HTTPS or SSH, but it is recommended that that you use SSH: first ensure that you have generated an SSH key pair on your local machine and add the public key of that pair to your GitHub account (use the GitHub guide at https://help.github.com/articles/connecting-to-github-with-ssh/). Then run

    git clone --recursive git+ssh://git@github.com/OasisLMF/omdk

To clone over HTTPS use

    git clone --recursive https://github.com/OasisLMF/omdk

You may receive a password prompt - to bypass the password prompt use

    git clone --recursive https://<GitHub user name:GitHub password>@github.com/OasisLMF/omdk

The `--recursive` option ensures the cloned repository contains the necessary Oasis repositories <a href="https://github.com/OasisLMF/oasis_utils" target="_blank">`oasis_utils`</a> as Git submodules.

# Sphinx Docs

This repository is enabled with <a href="https://pypi.python.org/pypi/Sphinx" target="_blank">Sphinx</a> documentation for the Python modules, and the documentation is published to <a href="https://oasislmf.github.io/OasisLMF/omdk/" target="_blank">https://oasislmf.github.io/omdk</a> automatically via GitHub pages on updates to the GitHub repository.

## Setting up Sphinx

Firstly, to work on the Sphinx docs for this package you must have Sphinx installed on your system or in your virtual environment (`virtualenv` is recommended).

You should also clone the Oasis publication repository <a href="https://github.com/OasisLMF/OasisLMF.github.io" target="_blank">OasisLMF.github.io</a>.

## Building and publishing

The Sphinx documentation source files are reStructuredText files, and are contained in the `docs` subfolder, which also contains the Sphinx configuration file `conf.py` and the `Makefile` for the build. To do a new build make sure you are in the `docs` subfolder and run

    make html

You should see a new set of HTML files and assets in the `_build/html` subfolder (the build directory can be changed to `docs` itself in the `Makefile` but that is not recommended). The `docs` subfolder should always contain the latest copy of the built HTML and assets so first copy the files from `_build/html` to `docs` using

    cp -R _build/html/* .

Add and commit these files to the local repository, and then update the remote repository on GitHub - GitHub pages will automatically publish the new documents to the documentation site https://oasislmf.github.io/omdk/.

# First Steps

After cloning the repository (see the GitHub instructions on repository home page) and entering the repository folder you should install the package requirements using

    sudo pip install -r requirements.txt

(You may need to omit the `sudo` if you are in a virtual environment.)

Provided that `sys.path` contains the absolute path to the repository folder you can now import the package or its components in the normal way.

# Generating Oasis Files

This repository provides an executable script called `oasis_files_generator.py`
for generating Oasis files for a given model, supplier and model version. The
resources required for the script are as follows:

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
    11. Oasis files directory path

The script can be executed in two ways: (1) directly by providing all the
resources in the script call using the following syntax:

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
                               -o '/path/to/oasis/files/directory'

or by providing the path to a JSON script config file which defines all
the script resources - the syntax for the latter option is:

    ./oasis_files_generator.py -f '/path/to/model/resources/JSON/config/file'

and the keys of the JSON config file, which correspond to the resources list,
above, should be named as follows:

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
    "output_dirpath"

The file and folder paths can be relative to the path of the script. If you've
cloned the OMDK repository then script configs for models can be placed in the
`script_config` subfolder, and the canonical exposures profiles can be placed
in the `canonical_exposures_profiles` subfolder.
