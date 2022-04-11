# 3rd party
import click
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from dom_toml.parser import BadConfigError
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from mkrecipe.__main__ import main
from tests.example_configs import MINIMAL_CONFIG

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
def test_mkrecipe(
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

	runner = CliRunner()
	result: Result

	with in_directory(tmp_pathplus):
		result = runner.invoke(main)

	assert result.stdout.strip() == "Recipe written to 'conda/meta.yaml'"
	assert result.exit_code == 0
	advanced_file_regression.check_file(tmp_pathplus / "conda" / "meta.yaml")

	with in_directory(tmp_pathplus):
		result = runner.invoke(main, args=["--type", "sdist"])

	assert result.stdout.strip() == "Recipe written to 'conda/meta.yaml'"
	assert result.exit_code == 0
	advanced_file_regression.check_file(tmp_pathplus / "conda" / "meta.yaml")

	with in_directory(tmp_pathplus):
		result = runner.invoke(main, args=["-t", "sdist"])

	assert result.stdout.strip() == "Recipe written to 'conda/meta.yaml'"
	assert result.exit_code == 0
	advanced_file_regression.check_file(tmp_pathplus / "conda" / "meta.yaml")

	with in_directory(tmp_pathplus):
		result = runner.invoke(main, args=["--type", "SDIST"])

	assert result.stdout.strip() == "Recipe written to 'conda/meta.yaml'"
	assert result.exit_code == 0
	advanced_file_regression.check_file(tmp_pathplus / "conda" / "meta.yaml")


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
def test_mkrecipe_wheel(
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

	runner = CliRunner()
	result: Result

	with in_directory(tmp_pathplus):
		result = runner.invoke(main, args=["--type", "wheel"])

	assert result.stdout.strip() == "Recipe written to 'conda/meta.yaml'"
	assert result.exit_code == 0
	advanced_file_regression.check_file(tmp_pathplus / "conda" / "meta.yaml")

	with in_directory(tmp_pathplus):
		result = runner.invoke(main, args=["-t", "wheel"])

	assert result.stdout.strip() == "Recipe written to 'conda/meta.yaml'"
	assert result.exit_code == 0
	advanced_file_regression.check_file(tmp_pathplus / "conda" / "meta.yaml")

	with in_directory(tmp_pathplus):
		result = runner.invoke(main, args=["--type", "WHEEL"])

	assert result.stdout.strip() == "Recipe written to 'conda/meta.yaml'"
	assert result.exit_code == 0
	advanced_file_regression.check_file(tmp_pathplus / "conda" / "meta.yaml")


_click_major_ver = click.__version__.split('.')[0]


def _param(label: str, expr: bool):
	return pytest.param(label, marks=pytest.mark.skipif(expr, reason="Output differs with click 8"))


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
@pytest.mark.parametrize("click_ver", [_param('8', _click_major_ver == '7'), _param('7', _click_major_ver != '7')])
def test_mkrecipe_bad_type(
		tmp_pathplus: PathPlus,
		pyproject_file: str,
		advanced_file_regression: AdvancedFileRegressionFixture,
		click_ver: str,
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

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(main, args=["--type", "egg"], catch_exceptions=False)

	assert result.exit_code == 2
	result.check_stdout(advanced_file_regression)


class TestHandleTracebacks:

	@pytest.mark.parametrize(
			"toml_config",
			[
					pytest.param('', id="empty"),
					pytest.param('[build-system]\nrequires = ["setuptools", "wheel"]', id="build-system"),
					pytest.param('[tool.whey]\nlicense-key = "MIT"', id="tool.whey"),
					]
			)
	def test_no_project_table(self, toml_config: str, tmp_pathplus: PathPlus) -> None:
		runner = CliRunner()
		(tmp_pathplus / "pyproject.toml").write_clean(toml_config)
		expected_error = pytest.raises(KeyError, match="'project' table not found in .*")

		with in_directory(tmp_pathplus):

			with expected_error:
				runner.invoke(main, args="-T", catch_exceptions=False)

			with expected_error:
				runner.invoke(main, args="--traceback", catch_exceptions=False)

			result = runner.invoke(main)
			assert result.exit_code == 1
			assert result.stdout == "KeyError: \"'project' table not found in 'pyproject.toml'\"\nAborted!\n"

	def test_no_requirements(self, tmp_pathplus: PathPlus) -> None:
		runner = CliRunner()
		(tmp_pathplus / "pyproject.toml").write_clean(MINIMAL_CONFIG)

		error_message = "'project.dependencies' was listed as a dynamic field but no 'requirements.txt' file was found."
		expected_error = pytest.raises(
				BadConfigError,
				match=error_message,
				)

		with in_directory(tmp_pathplus):

			with expected_error:
				runner.invoke(main, args="-T", catch_exceptions=False)

			with expected_error:
				runner.invoke(main, args="--traceback", catch_exceptions=False)

			result = runner.invoke(main)
			assert result.exit_code == 1
			assert result.stdout == f"BadConfigError: {error_message}\n" "Aborted!\n"
