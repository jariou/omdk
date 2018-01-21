.. omdk documentation master file, created by
   sphinx-quickstart on Thu Nov 30 10:56:52 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Oasis Model Development Kit (OMDK)
==================================

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