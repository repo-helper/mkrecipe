=====================
Configuration
=====================

``mkrecipe`` is configured in the ``pyproject.toml`` file defined in :pep:`517` and :pep:`518`.


``[project]``
-------------------

The metadata used by ``mkrecipe`` is defined in the ``[project]`` table, per :pep:`621`;
see that document for more details on the keys and their values.

As a minimum, the table should contain the keys ``name`` and ``version``.
It is recommended to define ``description``, ``authors`` and ``urls``.
If you list your project's requirements in a ``requirements.txt`` file, list ``dependencies`` as
`dynamic <https://www.python.org/dev/peps/pep-0621/#dynamic>`_; otherwise, they should be listed
under ``project.requirements``.


``[tool.mkrecipe]``
-------------------

.. conf:: package

	**Type**: :class:`str`

	The name of the package ``conda-build`` should import to check the package built correctly
	This defaults to `project.name <https://www.python.org/dev/peps/pep-0621/#name>`_ if unspecified.

	**Example**:

	.. code-block:: TOML

		[project]
		name = "domdf-python-tools"

		[tool.mkrecipe]
		package = "domdf_python_tools"


.. conf:: license-key

	**Type**: :class:`str`

	An identifier giving the project's license. This is used for the `License <https://packaging.python.org/specifications/core-metadata/#license>`_ field in the Core Metadata, and to add the appropriate `trove classifier <https://pypi.org/classifiers/>`_.

	It is recommended to use an `SPDX Identifier <https://spdx.org/licenses/>`_, but note that not all map to classifiers.

	**Example**:

	.. code-block:: TOML

		[tool.mkrecipe]
		license-key = "MIT"


.. raw:: latex

	\clearpage


.. conf:: conda-channels

	**Type**: :class:`list`\[:class:`str`\]

	A list of `conda channels <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/channels.html>`_.
	which provide the project's dependencies. Defaults to ``['conda-forge']`` if unspecified.

	**Example**:

	.. code-block:: TOML

		[tool.mkrecipe]
		conda-channels = [
			"domdfcoding",
			"conda-forge",
			"bioconda",
		]


.. conf:: extras

	**Type**: :class:`list`\[:class:`str`\] *or* the strings ``'all'`` or ``'none'``.

	A list of extras (AKA optional dependencies) to include as requirements in the conda package.

	* The special keyword ``'all'`` indicates all extras should be included.
	* The special keyword ``'none'`` indicates no extras should be included.

	Defaults to ``'none'`` if unspecified.

	**Examples**:

	.. code-block:: TOML

		[tool.mkrecipe]
		extras = [
			"pdf",
			"testing",
			"cli",
		]

	.. code-block:: TOML

		[tool.mkrecipe]
		extras = "all"

-----

``package`` and ``license-key`` can also be read from the ``[tool.whey]`` table if you use
`whey <https://whey.readthedocs.io/en/latest>`_ as the build backend and have defined those values there.
See the `whey documentation <https://whey.readthedocs.io/en/latest>`_ for more details.
