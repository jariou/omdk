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

# Requirements

## Python

After cloning the repository (see the GitHub instructions on repository home page) and entering the repository folder you should install the package Python requirements using

    sudo pip install -r requirements.txt

(You may need to omit the `sudo` if you are in a virtual environment.)

Provided that `sys.path` contains the absolute path to the repository folder you can now import the package or its components in the normal way.

## xtrans

There is one non-Python package requirement which is a .NET executable called `xtrans.exe` - this is used to convert source exposure files to canonical (Oasis) exposure files, and then also canonical exposure files to model exposure files. The source file `xrans.cs` is included in the `xtrans` subfolder. The executable requires a .NET engine like Mono (http://www.mono-project.com/) and the NDesk.Options library (http://www.ndesk.org/Options) which is included as a DLL in the `xtrans` subfolder. Assuming you've installed Mono you should be able to build the executable by running the `xtrans/make-trans` script - if successful it will be placed in `xtrans`.

## ktools

An installed ktools release suitable for your platform is required. You can obtain from

https://github.com/OasisLMF/ktools/releases

## Other requirements

Ensure that this repository is cloned into the same parent folder as any model keys server repositories (which would contain the lookup service source for the models of interest), and at the same level, e.g.

    <parent folder>/
    ├── omdk/
    ├── <model keys server repository>/
    ├── ...

# Building and running models

The repository provides a variety of Python tools to build, test and run models end-to-end, including performing individual steps in this process. These tools include:

* a Python class framework for working with Oasis models and model resources as Python objects (the `models` subpackage)
* a Python class framework for managing model exposures and resources, and also for generating Oasis files from these (the `exposures` subpackage)
* a Python factory class for instantiating keys lookup services for models, and generating and saving keys outputs from these lookup services
* executable scripts, based on these class frameworks, for writing keys outputs from model lookup services (`run_keys_lookup.py`), generating Oasis files from model source exposures and other resources (`generate_oasis_files.py`), and generating loss outputs for models (`generate_loss_outputs.py`). This includes a "master" script that can perform all these steps to run the model end-to-end (`run_model.py`).

## Generating keys outputs

`run_keys_lookup.py` is an executable script that can generate keys records and Oasis files keys for a model, given the following arguments (in no particular order)

    ./run_keys_lookup.py -k /path/to/keys/data
                         -v /path/to/model/version/csv/file
                         -l /path/to/lookup/service/package
                         -e /path/to/model/exposures/csv/file
                         -o /path/to/output/file
                         -f <output format - `oasis_keys` or `list_keys`>

When calling the script this way paths can be given relative to the script, in particular, file paths should include the filename and extension. The paths to the keys data, lookup service package, and model version file will usually be located in the model keys server (Git) repository, which would also contain the lookup service source code for the model (lookup service package. The lookup service package is usually located in the `src/keys_server` Python subpackage in the model keys serer repository (if it is managed by Oasis LMF).

It is also possible to run the script by defining these arguments in a JSON configuration file and calling the script using the path to this file using the option `-f`. In this case the paths should be given relative to the parent folder in which the model keys server repository is located.

    ./run_keys_lookup.py -f /path/to/keys/script/config/file

The JSON file should contain the following keys (in no particular order)

    "keys_data_path"
    "model_version_file_path"
    "lookup_package_path"
    "model_exposures_file_path"
    "output_file_path"
    "output_format"

and the values of these keys should be string paths, given relative to the parent folder in which the model keys server repository is located. The JSON file is usually placed in the model keys server repository.

## Generating Oasis files

`generate_oasis_files.py` is an executable script that can generate Oasis files for a model, given the following arguments (in no particular order)

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

When calling the script this way paths can be given relative to the script, in particular, file paths should include the filename and extension. The paths to the keys data, lookup service package, model version file, canonical exposures profile JSON, source exposures file, transformation and validation files, will usually be located in the model keys server repository.

It is also possible to run the script by defining these arguments in a JSON configuration file and calling the script using the path to this file using the option `-f`. In this case the paths should be given relative to the parent folder in which the model keys server repository is located.

    ./generate_oasis_files.py -f /path/to/model/resources/JSON/config/file

The JSON file contain the following keys (in no particular order)

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

and the values of these keys should be string paths, given relative to the parent folder in which the model keys server repository is located. The JSON file is usually placed in the model keys server repository.

## Generating loss outputs

`generate_loss_outputs.py` is an executable script that, given a model analysis settings JSON file, model data and some other parameters, can generate a (Bash) shell script which can be used to generate loss outputs for the model using the installed ktools framework, given the following arguments (in no particular order)

    ./generate_loss_outputs.py -j /path/to/analysis/settings/json/file
                               -s <ktools script name (without file extension)>
                               -m /path/to/model/data
                               -r /path/to/model/run/directory
                               -n <number of ktools calculation processes to use>

When calling the script this way paths can be given relative to the script, in particular, file paths should include the filename and extension. The ktools script name should not contain any filename extension, and the model run directory can be placed anywhere in the parent folder common to `omdk` and the model keys server repository.

It is also possible to run the script by defining these arguments in a JSON configuration file and calling the script using the path to this file using the option `-f`. In this case the paths should be given relative to the parent folder in which the model keys server repository is located.

    ./generate_loss_outputs.py -f /path/to/model/resources/JSON/config/file'

The JSON file should contain the following keys (in no particular order)

    "analysis_settings_json_file_path"
    "ktools_script_name"
    "model_data_path"
    "model_run_dir_path"
    "ktools_num_processes"

and the values of the path-related keys should be string paths, given relative to the parent folder in which the model keys server repository is located. The JSON file is usually placed in the model keys server repository.

**Note**: The output of `generate_loss_outputs.py` is an executable Bash shell script, containing ktools commands for generating loss outputs for the givem model and placed in the model run directory. You will have to execute the shell script in the model run directory in order to see the outputs. The model run directory must contain the analysis settings JSON file and either the actual model data or at least symlinked model data files (in the `static` subfolder). It must have the following structure

    ├── analysis_settings.json
    ├── fifo/
    ├── input/
    ├── output/
    ├── static/
    └── work/

The outputs are written in the `output` subfolder, and the model data should either be placed directly in the `static` subfolder or the actual folder should be symlinked to the `static` subfolder.

## Running a model end-to-end

`run_model.py` is an executable script that can run models end-to-end, i.e. generate ktools outputs from model resources, including keys data, model data, analysis settings etc., given the following arguments (in no particular order)

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

When calling the script this way paths can be given relative to the script, in particular, file paths should include the filename and extension. The paths to the keys data, lookup service package, model version file, canonical exposures profile JSON, source exposures file, transformation and validation files, and analysis settings JSON file, will usually be located in the model keys server repository. The ktools script name should not contain any filename extension, and the model run directory can be placed anywhere in the parent folder common to `omdk` and the model keys server repository.

It is also possible to run the script by defining these arguments in a JSON configuration file and calling the script using the path to this file using the option `-f`. In this case the paths should be given relative to the parent folder in which the model keys server repository is located.

    ./run_model.py -f /path/to/model/resources/JSON/config/file'

The JSON file should contain the following keys (in no particular order)

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

and the values of the path-related keys should be string paths, given relative to the parent folder in which the model keys server repository is located. The JSON file is usually placed in the model keys server repository.

**NOTE**:  As the JSON configuration files for `generate_oasis_files.py` and `generate_loss_outputs.py` defines a subset of the resources required for `run_model.py` you can use the `run_model.py` configuration file to also run `generate_oasis_files.py`.