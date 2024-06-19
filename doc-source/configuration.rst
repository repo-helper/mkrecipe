=====================
Configuration
=====================

``mkrecipe`` is configured in the ``pyproject.toml`` file defined in :pep:`517` and :pep:`518`.


``[project]``
-------------------

The metadata used by ``mkrecipe`` is defined in the ``[project]`` table, per :pep:`621`;
see that document for more details on the keys and their values.

As a minimum, the table should contain the keys :pep621:`name` and :pep621:`version`.
It is recommended to define :pep621:`description`, :pep621:`authors` and :pep621:`urls`.
If you list your project's requirements in a ``requirements.txt`` file,
list :pep621:`dependencies` as :pep621:`dynamic`; otherwise, they should be listed
under :pep621:`project.requirements <requirements>`.


``[tool.mkrecipe]``
-------------------

.. conf:: package

	**Type**: :toml:`String`

	The name of the package ``conda-build`` should import to check the package built correctly
	This defaults to :pep621:`project.name <name>` if unspecified.

	:bold-title:`Example:`

	.. code-block:: TOML

		[project]
		name = "domdf-python-tools"

		[tool.mkrecipe]
		package = "domdf_python_tools"


.. conf:: license-key

	**Type**: :toml:`String`

	An identifier giving the project's license. This is used for the :core-meta:`License`
	field in the Core Metadata, and to add the appropriate `trove classifier`_.

	It is recommended to use an `SPDX Identifier`_, but note that not all map to classifiers.

	.. _trove classifier: https://pypi.org/classifiers/
	.. _SPDX Identifier: https://spdx.org/licenses/

	:bold-title:`Example:`

	.. code-block:: TOML

		[tool.mkrecipe]
		license-key = "MIT"


.. raw:: latex

	\clearpage


.. conf:: conda-channels

	**Type**: :toml:`Array` of :toml:`strings <String>`

	A list of `conda channels <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/channels.html>`_.
	which provide the project's dependencies. Defaults to ``['conda-forge']`` if unspecified.

	:bold-title:`Example:`

	.. code-block:: toml

		[tool.mkrecipe]
		conda-channels = [
			"domdfcoding",
			"conda-forge",
			"bioconda",
		]


.. conf:: extras

	**Type**: :toml:`Array` of :toml:`strings <String>` *or* the strings ``'all'`` or ``'none'``.

	A list of extras (AKA :pep621:`optional dependencies <optional-dependencies>`)
	to include as requirements in the conda package.

	* The special keyword ``'all'`` indicates all extras should be included.
	* The special keyword ``'none'`` indicates no extras should be included.

	Defaults to ``'none'`` if unspecified.

	:bold-title:`Examples:`

	.. code-block:: toml

		[tool.mkrecipe]
		extras = [
			"pdf",
			"testing",
			"cli",
		]

	.. code-block:: TOML

		[tool.mkrecipe]
		extras = "all"

.. conf:: min-python-version

	**Type**: :toml:`String` or :toml:`Float`.

	The minimum Python 3.x version to consider requirements for.

	:bold-title:`Examples:`

	.. code-block:: toml

		[tool.mkrecipe]
		min-python-version = 3.6

.. conf:: max-python-version

	**Type**: :toml:`String` or :toml:`Float`.

	The maximum Python 3.x version to consider requirements for.

	:bold-title:`Examples:`

	.. code-block:: toml

		[tool.mkrecipe]
		max-python-version = 3.12


-----

:conf:`package` and :conf:`license-key` can also be read from the ``[tool.whey]`` table if you use
`whey <https://whey.readthedocs.io/en/latest>`_ as the build backend and have defined those values there.
See the `whey documentation <https://whey.readthedocs.io/en/latest>`_ for more details.
