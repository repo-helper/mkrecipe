#########
mkrecipe
#########

.. start short_desc

**A tool to create recipes for building conda packages from distributions on PyPI.**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/mkrecipe/latest?logo=read-the-docs
	:target: https://mkrecipe.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/repo-helper/mkrecipe/workflows/Docs%20Check/badge.svg
	:target: https://github.com/repo-helper/mkrecipe/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/repo-helper/mkrecipe/workflows/Linux/badge.svg
	:target: https://github.com/repo-helper/mkrecipe/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/repo-helper/mkrecipe/workflows/Windows/badge.svg
	:target: https://github.com/repo-helper/mkrecipe/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/repo-helper/mkrecipe/workflows/macOS/badge.svg
	:target: https://github.com/repo-helper/mkrecipe/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/repo-helper/mkrecipe/workflows/Flake8/badge.svg
	:target: https://github.com/repo-helper/mkrecipe/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/repo-helper/mkrecipe/workflows/mypy/badge.svg
	:target: https://github.com/repo-helper/mkrecipe/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/repo-helper/mkrecipe/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/repo-helper/mkrecipe/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/repo-helper/mkrecipe/master?logo=coveralls
	:target: https://coveralls.io/github/repo-helper/mkrecipe?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/repo-helper/mkrecipe?logo=codefactor
	:target: https://www.codefactor.io/repository/github/repo-helper/mkrecipe
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/mkrecipe
	:target: https://pypi.org/project/mkrecipe/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/mkrecipe?logo=python&logoColor=white
	:target: https://pypi.org/project/mkrecipe/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/mkrecipe
	:target: https://pypi.org/project/mkrecipe/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/mkrecipe
	:target: https://pypi.org/project/mkrecipe/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/mkrecipe?logo=anaconda
	:target: https://anaconda.org/domdfcoding/mkrecipe
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/mkrecipe?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/mkrecipe
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/repo-helper/mkrecipe
	:target: https://github.com/repo-helper/mkrecipe/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/repo-helper/mkrecipe
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/repo-helper/mkrecipe/v0.6.0.post1
	:target: https://github.com/repo-helper/mkrecipe/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/repo-helper/mkrecipe
	:target: https://github.com/repo-helper/mkrecipe/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2023
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/mkrecipe
	:target: https://pypi.org/project/mkrecipe/
	:alt: PyPI - Downloads

.. end shields

Installation
--------------

.. start installation

``mkrecipe`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install mkrecipe

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels https://conda.anaconda.org/conda-forge
		$ conda config --add channels https://conda.anaconda.org/domdfcoding

	* Then install

	.. code-block:: bash

		$ conda install mkrecipe

.. end installation


Usage
-----------

``mkrecipe`` is configured in ``pyproject.toml``. See `the documentation`_ for more information.

.. _the documentation: https://mkrecipe.readthedocs.io/en/latest/configuration.html

``mkrecipe`` can then be run with the ``mkrecipe`` command when in the project directory.
This will write the conda recipe to ``./conda/meta.yaml``.
The output directory can be customised using the ``-o / --outfile`` option.
