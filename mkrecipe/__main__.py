#!/usr/bin/env python3
#
#  __main__.py
"""
A tool to create recipes for building conda packages from distributions on PyPI.
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
import sys
from typing import TYPE_CHECKING

# 3rd party
import click
from consolekit import click_command
from consolekit.options import DescribedArgument, auto_default_option
from consolekit.tracebacks import handle_tracebacks, traceback_option

# this package
from mkrecipe import __version__

if TYPE_CHECKING:
	# 3rd party
	from domdf_python_tools.typing import PathLike
	from typing_extensions import Literal

__all__ = ("main", )


@click.version_option(__version__)
@traceback_option()
@auto_default_option(
		"-t",
		"--type",
		"artifact_type",
		type=click.Choice(["sdist", "wheel"], case_sensitive=False),
		help="The type of release artifact to build the conda package from.",
		show_default=True,
		)
@auto_default_option("-o", "--outfile", type=click.STRING, help="The output file.", show_default=True)
@click.argument(
		"project",
		type=click.STRING,
		default='.',
		description="The project to create the recipe for.",
		cls=DescribedArgument,
		)
@click_command()
def main(
		project: "PathLike" = '.',
		outfile: str = "conda/meta.yaml",
		artifact_type: "Literal['sdist', 'wheel']" = "sdist",
		show_traceback: bool = False,
		) -> None:
	"""
	Make a conda recipe for the given project.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus
	from pyproject_parser.cli import ConfigTracebackHandler

	# this package
	from mkrecipe import MaryBerry

	with handle_tracebacks(show_traceback, ConfigTracebackHandler):
		recipe_file = PathPlus(outfile)
		recipe_file.parent.maybe_make(parents=True)

		if artifact_type == "sdist":
			recipe = MaryBerry(project).make()
		elif artifact_type == "wheel":
			recipe = MaryBerry(project).make_for_wheel()
		else:  # pragma: no cover
			# Click should handle this case for us
			raise click.BadOptionUsage("type", f"Unknown value for '--type': {artifact_type}")

		recipe_file.write_clean(recipe)
		click.echo(f"Recipe written to {recipe_file.as_posix()!r}")


if __name__ == "__main__":
	sys.exit(main())

# TODO: command to enable channels in .condarc for the environment
# Environment prefixed is $CONDA_PREFIX
# config is in .condarc in $CONDA_PREFIX
# Needs yaml parser
# https://docs.conda.io/projects/conda/en/master/user-guide/configuration/use-condarc.html
