Repository Management
=====================

Cloning the repository
----------------------

You can clone this repository from GitHub using HTTPS or SSH, but it is
recommended that that you use SSH: first ensure that you have generated
an SSH key pair on your local machine and add the public key of that
pair to your GitHub account (use the GitHub guide at
https://help.github.com/articles/connecting-to-github-with-ssh/). Then
run

::

    git clone --recursive git+ssh://git@github.com/OasisLMF/omdk

To clone over HTTPS use

::

    git clone --recursive https://github.com/OasisLMF/omdk

You may receive a password prompt - to bypass the password prompt use

::

    git clone --recursive https://<GitHub user name:GitHub password>@github.com/OasisLMF/omdk

The ``--recursive`` option ensures the cloned repository contains the
necessary Oasis repositories \ ``oasis_utils``\  as Git submodules.
