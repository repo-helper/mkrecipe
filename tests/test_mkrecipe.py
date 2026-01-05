# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from mkrecipe import MaryBerry, make_recipe

configs_dir = PathPlus(__file__).parent / "configs"


@pytest.mark.parametrize(
		"pyproject_file",
		[
				"consolekit.pyproject.toml",
				"sphinx-toolbox.pyproject.toml",
				"flake8-encodings.pyproject.toml",
				"importcheck.pyproject.toml",
				"mathematical.pyproject.toml",
				]
		)
def test_make_recipe(
		tmp_pathplus: PathPlus,
		pyproject_file: str,
		advanced_file_regression: AdvancedFileRegressionFixture,
		) -> None:
	(tmp_pathplus / "pyproject.toml").write_text((configs_dir / pyproject_file).read_text())
	(tmp_pathplus / "requirements.txt").write_lines([
			"click>=7.1.2",
			'colorama>=0.4.3; python_version < "3.10"',
			"deprecation-alias>=0.1.1",
			"domdf-python-tools>=2.5.1",
			"mistletoe>=0.7.2",
			"typing-extensions>=3.7.4.3",
			'cryptography==3.3.2; platform_python_implementation != "CPython"',
			])

	make_recipe(tmp_pathplus, tmp_pathplus / "recipe.yaml")
	advanced_file_regression.check_file(tmp_pathplus / "recipe.yaml")


@pytest.mark.parametrize(
		"pyproject_file",
		[
				"consolekit.pyproject.toml",
				"sphinx-toolbox.pyproject.toml",
				"flake8-encodings.pyproject.toml",
				"importcheck.pyproject.toml",
				"mathematical.pyproject.toml",
				"github3-utils.pyproject.toml",
				]
		)
def test_MaryBerry_make(
		tmp_pathplus: PathPlus,
		pyproject_file: str,
		advanced_file_regression: AdvancedFileRegressionFixture,
		) -> None:
	(tmp_pathplus / "pyproject.toml").write_text((configs_dir / pyproject_file).read_text())
	(tmp_pathplus / "requirements.txt").write_lines([
			"click>=7.1.2",
			'colorama>=0.4.3; python_version < "3.10"',
			"deprecation-alias>=0.1.1",
			"domdf-python-tools>=2.5.1",
			"mistletoe>=0.7.2",
			"typing-extensions>=3.7.4.3",
			'cryptography==3.3.2; platform_system != "Linux" and platform_python_implementation != "CPython"',
			])

	recipe = MaryBerry(tmp_pathplus).make()

	advanced_file_regression.check(recipe, extension=".yaml")


@pytest.mark.parametrize(
		"pyproject_file",
		[
				"consolekit.pyproject.toml",
				"sphinx-toolbox.pyproject.toml",
				"flake8-encodings.pyproject.toml",
				"importcheck.pyproject.toml",
				"mathematical.pyproject.toml",
				]
		)
def test_MaryBerry_make_for_wheel(
		tmp_pathplus: PathPlus,
		pyproject_file: str,
		advanced_file_regression: AdvancedFileRegressionFixture,
		) -> None:
	(tmp_pathplus / "pyproject.toml").write_text((configs_dir / pyproject_file).read_text())
	(tmp_pathplus / "requirements.txt").write_lines([
			"click>=7.1.2",
			'colorama>=0.4.3; python_version < "3.10"',
			"deprecation-alias>=0.1.1",
			"domdf-python-tools>=2.5.1",
			"mistletoe>=0.7.2",
			"typing-extensions>=3.7.4.3",
			])

	recipe = MaryBerry(tmp_pathplus).make_for_wheel()

	advanced_file_regression.check(recipe, extension=".yaml")
