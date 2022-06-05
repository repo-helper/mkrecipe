#!/usr/bin/env python3
#
#  config.py
"""
:pep:`621` configuration parser.

.. versionchanged:: 0.2.0  ``BuildSystemParser`` moved to :mod:`pyproject_parser.parsers`
.. autosummary-widths:: 5/16 11/16
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from typing import Any, ClassVar, Dict, List, Union

# 3rd party
import dom_toml
import whey.config
from dom_toml.parser import TOML_TYPES, AbstractConfigParser, BadConfigError, construct_path
from domdf_python_tools.iterative import natmin
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.typing import PathLike
from packaging.specifiers import Specifier
from pyproject_parser.parsers import BuildSystemParser, name_re
from pyproject_parser.type_hints import ProjectDict
from shippinglabel.requirements import ComparableRequirement, combine_requirements, read_requirements
from typing_extensions import Literal

__all__ = ("MkrecipeParser", "PEP621Parser", "load_toml")


class PEP621Parser(whey.config.PEP621Parser):
	"""
	Parser for :pep:`621` metadata from ``pyproject.toml``.
	"""

	defaults: ClassVar[Dict[str, Any]] = {
			"description": None,
			"requires-python": ">=3.6",
			}
	factories = {
			"authors": list,
			"maintainers": list,
			"urls": dict,
			"dependencies": list,
			"optional-dependencies": dict,
			}
	keys: List[str] = [
			"name",
			"version",
			"description",
			"authors",
			"maintainers",
			"urls",
			"dependencies",
			"optional-dependencies",
			"requires-python",
			]

	@staticmethod
	def parse_name(config: Dict[str, TOML_TYPES]) -> str:
		"""
		Parse the `name <https://www.python.org/dev/peps/pep-0621/#name>`_ key.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		# preserve underscores, dots and hyphens, as conda doesn't treat them as equivalent.
		normalized_name = config["name"].lower()

		# https://packaging.python.org/specifications/core-metadata/#name
		if not name_re.match(normalized_name):
			raise BadConfigError("The value for 'project.name' is invalid.")

		return normalized_name

	def parse(  # type: ignore[override]
		self,
		config: Dict[str, TOML_TYPES],
		set_defaults: bool = False,
		) -> ProjectDict:
		"""
		Parse the TOML configuration.

		:param config:
		:param set_defaults: If :py:obj:`True`, the values in
			:attr:`dom_toml.parser.AbstractConfigParser.defaults` and
			:attr:`dom_toml.parser.AbstractConfigParser.factories`
			will be set as defaults for the returned mapping.

		:rtype:

		.. latex:clearpage::
		"""

		dynamic_fields = config.get("dynamic", [])

		if "name" in dynamic_fields:
			raise BadConfigError("The 'project.name' field may not be dynamic.")
		elif "name" not in config:
			raise BadConfigError("The 'project.name' field must be provided.")

		if "version" in dynamic_fields:
			raise BadConfigError("The 'project.version' field may not be dynamic.")
		elif "version" not in config:
			raise BadConfigError("The 'project.version' field must be provided.")

		if "dependencies" not in config and "dependencies" not in dynamic_fields:
			raise BadConfigError("The 'project.dependencies' field must be provided or marked as 'dynamic'")

		return self._parse(config, set_defaults)


class MkrecipeParser(AbstractConfigParser):
	"""
	Parser for the ``[tool.mkrecipe]`` table from ``pyproject.toml``.

	.. autosummary-widths:: 6/16
	"""

	table_name = ("tool", "mkrecipe")

	# Don't add any options shared with tool.whey
	defaults = {"extras": "none", "conda-channels": ("conda-forge", )}

	def parse_package(self, config: Dict[str, TOML_TYPES]) -> str:
		"""
		Parse the ``package`` key, giving the name of the importable package.

		This defaults to `project.name <https://www.python.org/dev/peps/pep-0621/#name>`_ if unspecified.

		:param config: The unparsed TOML config for the ``[tool.mkrecipe]`` table.
		"""

		package = config["package"]

		self.assert_type(package, str, [*self.table_name, "package"])

		return package

	def parse_license_key(self, config: Dict[str, TOML_TYPES]) -> str:
		"""
		Parse the ``license-key`` key, giving the identifier of the project's license. Optional.

		:param config: The unparsed TOML config for the ``[tool.mkrecipe]`` table.
		"""

		license_key = config["license-key"]

		self.assert_type(license_key, str, [*self.table_name, "license-key"])

		return license_key

	def parse_conda_channels(self, config: Dict[str, TOML_TYPES]) -> List[str]:
		r"""
		Parse the ``conda-channels`` key, giving a list of required conda channels to build and use the package.

		:param config: The unparsed TOML config for the ``[tool.mkrecipe]`` table.

		:rtype:

		.. latex:clearpage::
		"""

		channels = config["conda-channels"]

		for idx, impl in enumerate(channels):
			self.assert_indexed_type(impl, str, [*self.table_name, "conda-channels"], idx=idx)

		return channels

	def parse_extras(self, config: Dict[str, TOML_TYPES]) -> Union[Literal["all"], Literal["none"], List[str]]:
		"""
		Parse the ``extras`` key, giving a list of extras to include as requirements in the conda package.

		* The special keyword ``'all'`` indicates all extras should be included.
		* The special keyword ``'none'`` indicates no extras should be included.

		:param config: The unparsed TOML config for the ``[tool.mkrecipe]`` table.
		"""

		extras = config["extras"]

		path_elements = (*self.table_name, "extras")

		if isinstance(extras, str):
			extras_lower = extras.lower()
			if extras_lower == "all":
				return "all"
			elif extras_lower == "none":
				return "none"
			else:
				raise BadConfigError(
						f"Invalid value for [{construct_path(path_elements)}]: "
						"Expected 'all', 'none' or a list of strings."
						)

		for idx, impl in enumerate(extras):
			self.assert_indexed_type(impl, str, path_elements, idx=idx)

		return extras

	@property
	def keys(self) -> List[str]:
		"""
		The keys to parse from the TOML file.
		"""

		return [
				"package",
				"license-key",
				"conda-channels",
				"extras",
				]


def load_toml(filename: PathLike) -> Dict[str, Any]:  # TODO: TypedDict
	"""
	Load the ``mkrecipe`` configuration mapping from the given TOML file.

	:param filename:
	"""

	filename = PathPlus(filename)

	project_dir = filename.parent
	config = dom_toml.load(filename)

	parsed_config: Dict[str, Any] = {}
	tool_table = config.get("tool", {})

	with in_directory(filename.parent):

		parsed_config.update(BuildSystemParser().parse(config.get("build-system", {}), set_defaults=True))
		parsed_config.update(whey.config.WheyParser().parse(tool_table.get("whey", {})))
		parsed_config.update(MkrecipeParser().parse(tool_table.get("mkrecipe", {}), set_defaults=True))

		if "project" in config:
			parsed_config.update(PEP621Parser().parse(config["project"], set_defaults=True))
		else:
			raise KeyError(f"'project' table not found in '{filename!s}'")

	# set defaults
	parsed_config.setdefault("package", config["project"]["name"].split('.', 1)[0])
	parsed_config.setdefault("license-key", None)
	parsed_config.setdefault("python-versions", None)

	dynamic_fields = parsed_config.get("dynamic", [])

	if "requires-python" in dynamic_fields and parsed_config["python-versions"]:
		parsed_config["requires-python"] = Specifier(f">={natmin(parsed_config['python-versions'])}")

	if "dependencies" in dynamic_fields:
		if (project_dir / "requirements.txt").is_file():
			dependencies = read_requirements(project_dir / "requirements.txt", include_invalid=True)[0]
			parsed_config["dependencies"] = sorted(combine_requirements(dependencies))
		else:
			raise BadConfigError(
					"'project.dependencies' was listed as a dynamic field "
					"but no 'requirements.txt' file was found."
					)

	parsed_config["version"] = str(parsed_config["version"])
	parsed_config["requires"] = sorted(
			set(
					combine_requirements(
							parsed_config["requires"],
							ComparableRequirement("setuptools"),
							ComparableRequirement("wheel"),
							)
					)
			)

	return parsed_config
