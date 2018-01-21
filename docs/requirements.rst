Requirements
============

Python
------

After cloning the repository and entering the repository folder you
should install the package Python requirements using

::

    sudo pip install -r requirements.txt

(You may need to omit the ``sudo`` if you are in a virtual environment.)

Provided that ``sys.path`` contains the absolute path to the repository
folder you can now import the package or its components in the normal
way.

xtrans
------

There is one non-Python package requirement which is a .NET executable
called ``xtrans.exe`` - this is used to convert source exposure files to
canonical (Oasis) exposure files, and also canonical exposure files to
Oasis model exposure files. The source file ``xrans.cs`` is included in
the ``xtrans`` subfolder. The executable requires a .NET engine like
`Mono <http://www.mono-project.com>`_ and the `NDesk.Options library <http://www.ndesk.org/Options>`_ 
(included as a DLL in the ``xtrans`` subfolder). Assuming you've installed
Mono you should be able to build the executable by running the
``xtrans/make-trans`` script - if successful it will be placed in
``xtrans``.

ktools
------

An installed ktools release suitable for your platform is required. You
can obtain this from `https://github.com/OasisLMF/ktools/releases <https://github.com/OasisLMF/ktools/releases>`_.

Other requirements
------------------

Ensure that this repository is cloned into the same parent folder as any
model keys server repositories (which would contain the lookup service
source for the models of interest), and at the same level, e.g.

::

    <parent folder>/
    ├── omdk/
    ├── <model keys server repository>/
    ├── ...