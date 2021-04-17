# stdlib
import re
from typing import Type

# 3rd party
import dom_toml
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture
from dom_toml.parser import BadConfigError
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from mkrecipe.config import BuildSystemParser, MkrecipeParser, PEP621Parser, load_toml
from tests.example_configs import (
		AUTHORS,
		CLASSIFIERS,
		COMPLETE_A,
		COMPLETE_B,
		COMPLETE_PROJECT_A,
		DEPENDENCIES,
		ENTRY_POINTS,
		KEYWORDS,
		MAINTAINERS,
		MINIMAL_CONFIG,
		OPTIONAL_DEPENDENCIES,
		UNICODE,
		URLS
		)


@pytest.mark.parametrize(
		"toml_config",
		[
				pytest.param(MINIMAL_CONFIG, id="minimal"),
				pytest.param(f'{MINIMAL_CONFIG}\ndescription = "Lovely Spam! Wonderful Spam!"', id="description"),
				pytest.param(f'{MINIMAL_CONFIG}\nrequires-python = ">=3.8"', id="requires-python"),
				pytest.param(
						f'{MINIMAL_CONFIG}\nrequires-python = ">=2.7,!=3.0.*,!=3.2.*"',
						id="requires-python_complex"
						),
				pytest.param(KEYWORDS, id="keywords"),
				pytest.param(AUTHORS, id="authors"),
				pytest.param(MAINTAINERS, id="maintainers"),
				pytest.param(CLASSIFIERS, id="classifiers"),
				pytest.param(DEPENDENCIES, id="dependencies"),
				pytest.param(OPTIONAL_DEPENDENCIES, id="optional-dependencies"),
				pytest.param(URLS, id="urls"),
				pytest.param(ENTRY_POINTS, id="entry_points"),
				pytest.param(UNICODE, id="unicode"),
				pytest.param(COMPLETE_PROJECT_A, id="COMPLETE_PROJECT_A"),
				pytest.param(COMPLETE_A, id="COMPLETE_A"),
				pytest.param(COMPLETE_B, id="COMPLETE_B"),
				]
		)
def test_pep621_class_valid_config(
		toml_config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(toml_config)

	with in_directory(tmp_pathplus):
		config = PEP621Parser().parse(dom_toml.load(tmp_pathplus / "pyproject.toml")["project"])

	if "dependencies" in config:
		config["dependencies"] = list(map(str, config["dependencies"]))  # type: ignore
	if "optional-dependencies" in config:
		config["optional-dependencies"] = {
				k: list(map(str, v))  # type: ignore
				for k, v in config["optional-dependencies"].items()
				}

	if "requires-python" in config and config["requires-python"] is not None:
		config["requires-python"] = str(config["requires-python"])  # type: ignore
	if "version" in config and config["version"] is not None:
		config["version"] = str(config["version"])  # type: ignore

	advanced_data_regression.check(config)


@pytest.mark.parametrize(
		"config, expects, match",
		[
				pytest.param(
						'[project]\nname = "spam"',
						BadConfigError,
						"The 'project.version' field must be provided.",
						id="no_version"
						),
				pytest.param(
						'[project]\nversion = "2020.0.0"',
						BadConfigError,
						"The 'project.name' field must be provided.",
						id="no_name"
						),
				pytest.param(
						'[project]\ndynamic = ["name"]',
						BadConfigError,
						"The 'project.name' field may not be dynamic.",
						id="dynamic_name"
						),
				pytest.param(
						'[project]\nname = "spam"\ndynamic = ["version"]',
						BadConfigError,
						"The 'project.version' field may not be dynamic.",
						id="dynamic_version"
						),
				pytest.param(
						'[project]\nname = "spam"\nversion = "2020.0.0"',
						BadConfigError,
						"The 'project.dependencies' field must be provided or marked as 'dynamic'",
						id="no_dependencies"
						),
				pytest.param(
						'[project]\nname = "???????12345=============☃"\nversion = "2020.0.0"\ndynamic = ["dependencies"]',
						BadConfigError,
						"The value for 'project.name' is invalid.",
						id="bad_name"
						),
				pytest.param(
						'[project]\nname = "spam"\nversion = "???????12345=============☃"\ndynamic = ["dependencies"]',
						BadConfigError,
						re.escape("Invalid version: '???????12345=============☃'"),
						id="bad_version"
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\nauthors = [{{name = "Bob, Alice"}}]',
						BadConfigError,
						r"The 'project.authors\[0\].name' key cannot contain commas.",
						id="author_comma"
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\nmaintainers = [{{name = "Bob, Alice"}}]',
						BadConfigError,
						r"The 'project.maintainers\[0\].name' key cannot contain commas.",
						id="maintainer_comma"
						),
				pytest.param(
						f'[project]\nname = "spam"\nversion = "2020.0.0"\ndependencies = [1, 2, 3, 4, 5]',
						TypeError,
						r"Invalid type for 'project.dependencies\[0\]': expected <class 'str'>, got <class 'int'>",
						id="dependencies_wrong_type"
						),
				]
		)
def test_pep621parser_class_errors(config: str, expects: Type[Exception], match: str, tmp_pathplus: PathPlus):
	(tmp_pathplus / "pyproject.toml").write_clean(config)

	with in_directory(tmp_pathplus), pytest.raises(expects, match=match):
		PEP621Parser().parse(dom_toml.load(tmp_pathplus / "pyproject.toml")["project"])


@pytest.mark.parametrize(
		"toml_config",
		[
				pytest.param('[build-system]\nrequires = []', id="requires_nothing"),
				pytest.param('[build-system]\nrequires = ["whey"]', id="requires_whey"),
				pytest.param('[build-system]\nrequires = ["setuptools", "wheel"]', id="requires_setuptools"),
				pytest.param('[build-system]\nrequires = ["whey"]\nbuild-backend = "whey"', id="complete"),
				]
		)
def test_buildsystem_parser_valid_config(
		toml_config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(toml_config)
	config = BuildSystemParser().parse(dom_toml.load(tmp_pathplus / "pyproject.toml")["build-system"])

	config["requires"] = list(map(str, config["requires"]))  # type: ignore

	advanced_data_regression.check(config)


@pytest.mark.parametrize(
		"toml_config",
		[
				pytest.param('[tool.mkrecipe]\nlicense-key = "MIT"', id="license_key"),
				pytest.param('[tool.mkrecipe]\npackage = "domdf_python_tools"', id="package"),
				pytest.param('[tool.mkrecipe]\nextras = ["cli", "testing"]', id="extras"),
				pytest.param('[tool.mkrecipe]\nextras = "all"', id="extras_all"),
				pytest.param('[tool.mkrecipe]\nextras = "none"', id="extras_none"),
				pytest.param(
						'[tool.mkrecipe]\nconda-channels = ["domdfcoding", "conda-forge"]', id="conda_channels"
						),
				]
		)
def test_mkrecipe_parser_valid_config(
		toml_config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(toml_config)
	config = MkrecipeParser().parse(dom_toml.load(tmp_pathplus / "pyproject.toml")["tool"]["mkrecipe"])
	advanced_data_regression.check(config)


@pytest.mark.parametrize("toml_config", [
		pytest.param('[tool.mkrecipe]\nextras = "cli"', id="extras_cli"),
		])
def test_mkrecipe_parser_invalid_extras(
		toml_config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	with pytest.raises(BadConfigError, match=r"Invalid value for \[tool.mkrecipe.extras\]: "):
		MkrecipeParser().parse(dom_toml.loads(toml_config)["tool"]["mkrecipe"])


@pytest.mark.parametrize(
		"toml_config",
		[
				pytest.param('', id="empty"),
				pytest.param('[build-system]\nrequires = ["setuptools", "wheel"]', id="build-system"),
				pytest.param('[tool.whey]\nlicense-key = "MIT"', id="tool.whey"),
				]
		)
def test_load_toml_no_project_table(toml_config: str, tmp_pathplus: PathPlus):
	(tmp_pathplus / "pyproject.toml").write_clean(toml_config)

	with pytest.raises(KeyError, match="'project' table not found in .*"):
		load_toml(tmp_pathplus / "pyproject.toml")


def test_load_toml_no_requirements(tmp_pathplus: PathPlus):
	(tmp_pathplus / "pyproject.toml").write_clean(MINIMAL_CONFIG)

	with pytest.raises(
			BadConfigError,
			match="'project.dependencies' was listed as a dynamic field but no 'requirements.txt' file was found.",
			):
		load_toml(tmp_pathplus / "pyproject.toml")
