.. omdk documentation master file, created by
   sphinx-quickstart on Thu Nov 30 10:56:52 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Oasis Model Development Kit (OMDK)
==================================

The repository provides a variety of Python tools to build, test and run
models end-to-end, including performing individual steps in this
process. These tools include:

-  a Python class framework for working with Oasis models and model
   resources as Python objects (the ``models`` subpackage)
-  a Python class framework for managing model exposures and resources,
   and also for generating Oasis files from these (the ``exposures``
   subpackage)
-  a Python factory class for instantiating keys lookup services for
   models, and generating and saving keys outputs from these lookup
   services
-  executable scripts, based on these class frameworks, for writing keys
   outputs from model lookup services (``run_keys_lookup.py``),
   generating Oasis files from model source exposures and other
   resources (``generate_oasis_files.py``), and generating loss outputs
   for models (``generate_loss_outputs.py``). This includes a "master"
   script that can perform all these steps to run the model end-to-end
   (``run_model.py``).

The package documentation can be found at https://oasislmf.github.io/omdk/.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   repository-management
   sphinx
   requirements
   building-and-running-models
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`