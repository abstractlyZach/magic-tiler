from magic_tiler import toml_config


def test_toml():
    config_reader = toml_config.TomlConfig()
    config = config_reader.read("examples/centered_big.toml")
    assert config == {
        "screen": [
            {
                "children": [
                    {"size": 60, "command": "alacritty --title medium-window"},
                    {"size": 40, "command": "alacritty --title tiny-window"},
                ],
                "split": "horizontal",
                "size": 25,
            },
            {"size": 50, "command": "alacritty --title middle-panel"},
            {"size": 25, "command": "alacritty --title right-panel"},
        ],
        "split": "vertical",
    }
