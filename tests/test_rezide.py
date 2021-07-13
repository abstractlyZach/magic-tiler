from typing import Dict, List, NamedTuple
from unittest import mock

import pytest

from rezide import rezide
from rezide.utils import dtos


@pytest.fixture
def MockWindowManager(mocker):
    return mocker.patch("rezide.utils.sway.Sway")


@pytest.fixture
def MockMagicTiler(mocker):
    return mocker.patch("rezide.rezide.MagicTiler")


@pytest.fixture
def MockConfig(mocker):
    return mocker.patch("rezide.utils.configs.TomlConfig")


@pytest.fixture
def MockLayoutManager(mocker):
    return mocker.patch("rezide.utils.layouts.LayoutManager")


@pytest.fixture
def MockFilestore(mocker):
    return mocker.patch("rezide.utils.filestore.LocalFilestore")


# how do we even run an end-to-end test?? a sandboxed vm that runs a window manager?
@pytest.mark.skip
@pytest.mark.e2e
def test_rezide_script(click_runner):
    result = click_runner.invoke(rezide.main)
    assert result.exit_code == 0


class ClickTestParams(NamedTuple):
    """Store test parameters in a nice namedtuple"""

    cli_args: List[str]
    shell_env: Dict
    expected_parsed_env: dtos.Env


test_params = [
    ClickTestParams(
        cli_args=["open", "my_ide"],
        shell_env={"HOME": "abc", "XDG_CONFIG_HOME": "def"},
        expected_parsed_env=dtos.Env(home="abc", xdg_config_home="def"),
    ),
    # can we override CLI env variables?
    ClickTestParams(
        cli_args=[
            "--user-home-dir",
            "different_home",
            "--xdg-config-home-dir",
            "different_xdg",
            "open",
            "my_ide",
        ],
        shell_env={"HOME": "abc", "XDG_CONFIG_HOME": "def"},
        expected_parsed_env=dtos.Env(
            home="different_home", xdg_config_home="different_xdg"
        ),
    ),
    ClickTestParams(
        cli_args=["-v", "open", "test_ide"],
        shell_env={"HOME": "abc", "XDG_CONFIG_HOME": "def"},
        expected_parsed_env=dtos.Env(home="abc", xdg_config_home="def"),
    ),
    ClickTestParams(
        cli_args=["-vv", "open", "super-verbose"],
        shell_env={"HOME": "abc", "XDG_CONFIG_HOME": "def"},
        expected_parsed_env=dtos.Env(home="abc", xdg_config_home="def"),
    ),
]


# I don't like mocking so many things, but I'm not sure how to do DI
# when we're using Click
@pytest.mark.parametrize("test_parameters", test_params)
def test_successful_script(
    click_runner,
    MockWindowManager,
    MockMagicTiler,
    MockConfig,
    MockLayoutManager,
    MockFilestore,
    test_parameters,
):
    """Verify that we're setting up dependencies and calling MagicTiler correctly"""
    result = click_runner.invoke(
        rezide.main,
        test_parameters.cli_args,
        env=test_parameters.shell_env,
    )
    assert result.exit_code == 0, result.exception
    assert "" == result.output, result.exception
    MockConfig.assert_called_once_with(
        MockFilestore(), env=test_parameters.expected_parsed_env
    )
    MockMagicTiler.assert_called_once_with(
        test_parameters.expected_parsed_env, MockLayoutManager()
    )
    MockMagicTiler.return_value.run.assert_called_once_with(
        test_parameters.cli_args[-1]
    )


def test_run():
    env = dtos.Env(home="abc", xdg_config_home="def")
    layout = mock.MagicMock()
    application = rezide.MagicTiler(env, layout)
    application.run("my_ide")
    layout.select.assert_called_once_with("my_ide")
    layout.spawn_windows.assert_called_once_with()


def test_list_layouts(
    click_runner,
    MockConfig,
    MockFilestore,
):
    MockConfig.return_value.to_dict.return_value = {
        "layout 0": {"is_layout": True},
        "not a layout 0 ": {"size": 9999},
        "layout 1": {"is_layout": True, "children": [1, 2, 3]},
        "not a layout 1": {
            "layout": "horizontal",
            "children": ["a", "b", "c"],
            "sizes": [50, 25, 25],
        },
        "layout 2": {
            "is_layout": True,
            "layout": "horizontal",
            "children": ["a", "b", "c"],
            "sizes": [50, 25, 25],
        },
    }
    result = click_runner.invoke(
        rezide.main, ["-c", "abc", "--user-home-dir", "def", "list-layouts"]
    )
    MockConfig.assert_called_once_with(
        MockFilestore(),
        env=dtos.Env(home="def", xdg_config_home="abc"),
    )
    for number in range(3):
        assert f"layout {number}" in result.output


# TODO: add integration tests where we fail due to invalid config files