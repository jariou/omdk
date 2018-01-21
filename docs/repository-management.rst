Repository Management
=====================

Cloning the repository
----------------------

You can clone this repository from GitHub using HTTPS or SSH. Before
doing this you must generate an SSH key pair on your local machine and
add the public key of that pair to your GitHub account (use the GitHub
guide at
https://help.github.com/articles/connecting-to-github-with-ssh/). To
clone over SSH use

::

    git clone --recursive git+ssh://git@github.com/OasisLMF/omdk

To clone over HTTPS use

::

    git clone --recursive https://<GitHub user name:GitHub password>@github.com/OasisLMF/omdk

The ``--recursive`` option ensures the cloned repository contains `oasis_utils <https://github.com/OasisLMF/oasis_utils>`_ 
as a Git submodule, which is a requirement.