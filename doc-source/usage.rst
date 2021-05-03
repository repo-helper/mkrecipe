=====================
Command Line Usage
=====================

mkrecipe
----------

.. click:: mkrecipe.__main__:main
	:prog: mkrecipe
	:nested: none

.. versionchanged:: 0.3.0  Added the :option:`-t / --type <-t>` option which allows building conda packages from wheels rather than sdists. This is useful to avoid circular dependencies when the project is a dependency of the build tool.
