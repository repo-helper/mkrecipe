#!/usr/bin/env python3
#
#  __init__.py
"""
A tool to create recipes for building conda packages from distributions on PyPI.
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
import re
import time
from itertools import chain
from typing import Any, Dict, Iterable, List

# 3rd party
import click
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from jinja2 import BaseLoader, Environment, StrictUndefined
from packaging.requirements import InvalidRequirement
from shippinglabel.conda import prepare_requirements, validate_requirements
from shippinglabel.pypi import get_sdist_url
from shippinglabel.requirements import ComparableRequirement, combine_requirements
from whey.config.whey import license_lookup

# this package
from mkrecipe.config import load_toml

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.2.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["MaryBerry", "make_recipe"]


class MaryBerry:
	# Get it?
	"""
	Builder of Conda ``meta.yaml`` recipes.

	:param project_dir: The project directory.
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

	def get_sdist_url(self) -> str:
		"""
		Returns the URL of the project's source distribution on PyPI.
		"""

		for retry in range(0, 4):
			# TODO: perhaps add an option or environment variable
			try:
				return get_sdist_url(self.config["name"], self.config["version"])
			except InvalidRequirement as e:
				click.echo(f"{e} Trying again in 10s", err=True)
				time.sleep(10)
		else:
			raise InvalidRequirement(
					f"Cannot find {self.config['name']} version {self.config['version']} on PyPI."
					)

	def get_runtime_requirements(self) -> List[ComparableRequirement]:
		"""
		Returns a list of the project's runtime requirements.
		"""

		extras = []

		for extra in self.config["extras"]:
			extras.extend(list(map(str, self.config["optional-dependencies"].get(extra, ()))))

		extra_requirements = [ComparableRequirement(r) for r in extras]

		all_requirements = prepare_requirements(chain(self.config["dependencies"], extra_requirements))
		all_requirements = validate_requirements(all_requirements, self.config["conda-channels"])

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

		conda_description = self.config["description"]
		conda_channels = tuple(self.config["conda-channels"])

		if conda_channels:
			conda_description += "\n\n\n"
			conda_description += "Before installing please ensure you have added the following channels: "
			conda_description += ", ".join(conda_channels)
			conda_description += '\n'

		return conda_description

	def get_urls(self) -> Iterable[str]:
		"""
		Returns an iterable of URL entries for the "about" section of the recipe.
		"""

		for label, url in self.config["urls"].items():
			if label.lower() == "homepage":
				yield f"home: {str(url)!r}"
			# elif re.match("issue[s\s_-]*(tracker)?", label, flags=re.IGNORECASE):
			# 	yield f"home: {str(url)!r}"
			elif re.match(r"source[\s_-]*(code)?", label, flags=re.IGNORECASE):
				yield f"dev_url: {str(url)!r}"
			elif re.match("doc(s|umentation)?", label, flags=re.IGNORECASE):
				yield f"doc_url: {str(url)!r}"


def make_recipe(project_dir: PathLike, recipe_file: PathLike) -> None:
	"""
	Make a Conda ``meta.yaml`` recipe.

	:param project_dir: The project directory.
	:param recipe_file: The file to save the recipe as.
	"""

	recipe_file = PathPlus(recipe_file)
	recipe_file.parent.maybe_make(parents=True)
	recipe_file.write_clean(MaryBerry(project_dir).make())
