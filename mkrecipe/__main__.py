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
from consolekit.options import auto_default_option
from consolekit.tracebacks import handle_tracebacks, traceback_option

if TYPE_CHECKING:
	# 3rd party
	from domdf_python_tools.typing import PathLike

__all__ = ["main"]


@traceback_option()
@auto_default_option("-o", "--outfile", type=click.STRING, help="The output file.", show_default=True)
@click.argument("project", type=click.STRING, default='.')
@click_command()
def main(
		project: "PathLike" = '.',
		outfile: str = "conda/meta.yaml",
		show_traceback: bool = False,
		):
	"""
	Make a conda recipe for the given project.
	"""

	# 3rd party
	from pyproject_parser.cli import ConfigTracebackHandler

	# this package
	from mkrecipe import make_recipe

	with handle_tracebacks(show_traceback, ConfigTracebackHandler):
		make_recipe(project, outfile)
		click.echo(f"Recipe written to {outfile}")


if __name__ == "__main__":
	sys.exit(main())

# TODO: command to enable channels in .condarc for the environment
# Environment prefixed is $CONDA_PREFIX
# config is in .condarc in $CONDA_PREFIX
# Needs yaml parser
# https://docs.conda.io/projects/conda/en/master/user-guide/configuration/use-condarc.html
