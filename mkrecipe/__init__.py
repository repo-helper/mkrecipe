#!/usr/bin/env python3
#
#  __init__.py
"""
A tool to create recipes for building conda packages from distributions on PyPI.

.. autosummary-widths:: 7/16
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import os
import re
from itertools import chain
from time import sleep
from typing import Any, Callable, Dict, Iterable, List, Union

# 3rd party
from click import echo
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from jinja2 import BaseLoader, Environment, StrictUndefined
from packaging.requirements import InvalidRequirement
from packaging.version import Version
from shippinglabel.requirements import ComparableRequirement, combine_requirements
from shippinglabel_conda import make_conda_description, prepare_requirements, validate_requirements
from shippinglabel_pypi import get_sdist_url, get_wheel_url
from whey.config.whey import license_lookup

# this package
from mkrecipe.config import load_toml

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.6.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ("MaryBerry", "make_recipe")

RETRIES = int(os.environ.get("MKRECIPE_HTTP_RETRIES", 3)) + 1
RETRY_DELAY = int(os.environ.get("MKRECIPE_RETRY_DELAY", 10))


class MaryBerry:
	# Get it?
	"""
	Builder of Conda ``meta.yaml`` recipes.

	:param project_dir: The project directory.

	.. autosummary-widths:: 6/16
	"""

	def __init__(self, project_dir: PathLike) -> None:
		self.project_dir = PathPlus(project_dir)
		self.config = self.load_config()

	def load_config(self) -> Dict[str, Any]:
		"""
		Load the ``mkrecipe`` configuration.
		"""

		return load_toml(self.project_dir / "pyproject.toml")

	def make(self) -> str:
		"""
		Make the recipe.

		:returns: The ``meta.yaml`` recipe as a string.
		"""

		# find the download URL
		sdist_url = self.get_sdist_url()

		runtime_requirements = self.get_runtime_requirements()
		host_requirements = sorted(
				set(combine_requirements(
						runtime_requirements,
						*self.config["requires"],
						normalize_func=str,
						))
				)

		project_license = license_lookup.get(self.config["license-key"], self.config["license-key"])

		environment = Environment(loader=BaseLoader(), undefined=StrictUndefined)  # nosec: B701
		template = environment.from_string(importlib_resources.read_text("mkrecipe", "recipe_template.ymlt"))
		config = {k.replace('-', '_'): v for k, v in self.config.items()}

		return template.render(
				sdist_url=sdist_url,
				host_requirements=host_requirements,
				runtime_requirements=runtime_requirements,
				conda_full_description=self.make_conda_description(),
				url_lines=list(self.get_urls()),
				all_maintainers=sorted(self.get_maintainers()),
				project_license=project_license,
				**config,
				)

		# TODO: Entry points
		#  entry_points:
		#    - {{ import_name }} = {{ import_name }}:main
		#  skip_compile_pyc:
		#    - "*/templates/*.py"          # These should not (and cannot) be compiled

	def make_for_wheel(self) -> str:
		"""
		Make the recipe for creating a conda package from a wheel.

		.. versionadded:: 0.3.0

		:returns: The ``meta.yaml`` recipe as a string.
		"""

		# find the download URL
		wheel_url = self.get_wheel_url()

		runtime_requirements = self.get_runtime_requirements()
		host_requirements = sorted(
				set(combine_requirements(
						runtime_requirements,
						"setuptools",
						"wheel",
						normalize_func=str,
						))
				)

		project_license = license_lookup.get(self.config["license-key"], self.config["license-key"])

		environment = Environment(loader=BaseLoader(), undefined=StrictUndefined)  # nosec: B701
		template = environment.from_string(importlib_resources.read_text("mkrecipe", "recipe_template.ymlt"))
		config = {k.replace('-', '_'): v for k, v in self.config.items() if k != "requires"}

		return template.render(
				wheel_url=wheel_url,
				host_requirements=host_requirements,
				runtime_requirements=runtime_requirements,
				conda_full_description=self.make_conda_description(),
				url_lines=list(self.get_urls()),
				all_maintainers=sorted(self.get_maintainers()),
				project_license=project_license,
				requires=["setuptools", "wheel"],
				wheel=True,
				**config,
				)

	def get_sdist_url(self) -> str:
		"""
		Returns the URL of the project's source distribution on PyPI.
		"""

		sdist_url = self._try_again(get_sdist_url)

		if not sdist_url.endswith(".tar.gz"):
			raise InvalidRequirement(
					f"Cannot find source distribution for {self.config['name']} version {self.config['version']}."
					)

		return sdist_url

	def get_wheel_url(self) -> str:
		"""
		Returns the URL of the project's binary wheel on PyPI.

		.. versionadded:: 0.3.0
		"""

		wheel_url = self._try_again(get_wheel_url)

		if not wheel_url.endswith(".whl"):
			raise InvalidRequirement(
					f"Cannot find wheel for {self.config['name']} version {self.config['version']}."
					)

		return wheel_url

	def _try_again(self, func: Callable[[str, Union[str, int, Version]], str]) -> str:
		name, version = self.config["name"], self.config["version"]

		for retry in range(0, RETRIES):  # pylint: disable=W8202
			try:  # pylint: disable=R8203
				url = func(name, version)
				return url
			except InvalidRequirement as e:  # pragma: no cover  # pylint: disable=W8201
				echo(f"{e} Trying again in 10s", err=True)  # click.echo  # pylint: disable=W8201
				sleep(RETRY_DELAY)  # time.sleep  # pylint: disable=W8202

		raise InvalidRequirement(f"Cannot find {self.config['name']} version {self.config['version']} on PyPI.")

	def get_runtime_requirements(self) -> List[ComparableRequirement]:
		"""
		Returns a list of the project's runtime requirements.

		:rtype:

		.. latex:clearpage::
		"""

		extras: List[Union[str, ComparableRequirement]] = []

		if self.config["extras"] == "all":
			extras.extend(chain.from_iterable(self.config["optional-dependencies"].values()))
		elif self.config["extras"] == "none":
			pass
		else:
			for extra in self.config["extras"]:
				extras.extend(list(self.config["optional-dependencies"].get(extra, ())))

		extra_requirements = [ComparableRequirement(str(r)) for r in extras]

		# TODO: handle extras from the dependencies. Lookup the requirements in the wheel metadata.
		#  Perhaps wait until exposed in PyPI API
		all_requirements: List[ComparableRequirement] = []
		for req in chain(self.config["dependencies"], extra_requirements):  # pylint: disable=W8201
			if req.marker is not None:
				marker = str(req.marker).lower()
				if 'platform_system != "linux"' in marker:
					continue
				elif 'platform_python_implementation != "cpython"' in marker:
					continue

			all_requirements.append(req)

		all_requirements = validate_requirements(
				prepare_requirements(all_requirements),
				self.config["conda-channels"],
				)

		requirements_entries = [req for req in all_requirements if req and req != "numpy"]

		if [v.specifier for v in all_requirements if v == "numpy"]:
			requirements_entries.append(ComparableRequirement("numpy>=1.19.0"))

		return requirements_entries

	def get_maintainers(self) -> Iterable[str]:
		"""
		Returns an iterable over the names of the project's maintainers.
		"""

		all_maintainers = set()

		if self.config["maintainers"]:
			for maintainer in self.config["maintainers"]:
				if "name" in maintainer:
					all_maintainers.add(repr(maintainer["name"]))
		elif self.config["authors"]:
			for maintainer in self.config["authors"]:
				if "name" in maintainer:
					all_maintainers.add(repr(maintainer["name"]))

		return all_maintainers

	def make_conda_description(self) -> str:
		"""
		Create a description for the Conda package from its summary and a list of channels required to install it.
		"""

		return make_conda_description(self.config["description"], self.config["conda-channels"])

	def get_urls(self) -> Iterable[str]:
		"""
		Returns an iterable of URL entries for the "about" section of the recipe.
		"""

		for label, url in self.config["urls"].items():
			if label.lower() == "homepage":
				yield f"home: {str(url)!r}"
			# elif re.match("issue[s\s_-]*(tracker)?", label, flags=re.IGNORECASE):
			# 	yield f"home: {str(url)!r}"
			elif _source_code_re.match(label):  # pylint: disable=W8202
				yield f"dev_url: {str(url)!r}"
			elif _documentation_re.match(label):  # pylint: disable=W8202
				yield f"doc_url: {str(url)!r}"


_source_code_re = re.compile(r"source[\s_-]*(code)?", flags=re.IGNORECASE)
_documentation_re = re.compile(r"doc(s|umentation)?", flags=re.IGNORECASE)


def make_recipe(project_dir: PathLike, recipe_file: PathLike) -> None:
	"""
	Make a Conda ``meta.yaml`` recipe.

	:param project_dir: The project directory.
	:param recipe_file: The file to save the recipe as.
	"""

	recipe_file = PathPlus(recipe_file)
	recipe_file.parent.maybe_make(parents=True)
	recipe_file.write_clean(MaryBerry(project_dir).make())
