# reZIDE
<img src="docs/reZIDE.png" width="200" />

[![Tests](https://github.com/abstractlyZach/reZIDE/workflows/Tests/badge.svg)](https://github.com/abstractlyZach/reZIDE/actions?workflow=Tests)
[![Codecov](https://codecov.io/gh/abstractlyZach/reZIDE/branch/main/graph/badge.svg)](https://codecov.io/gh/abstractlyZach/reZIDE)
[![PyPI](https://img.shields.io/pypi/v/reZIDE.svg)](https://pypi.org/project/reZIDE/)

reZIDE will instantly create your own IDE. No need for tmux! Write your own
configurations easily or look to others' for inspiration: `link to configs`

## Notes
This project should work for both i3 and sway since it uses `i3ipc`. So whenever "i3" is used in this document, feel
free to replace it with "Sway" in your head if that's what you use.

## Motivation
Ever since I started using an ultrawide monitor in favor of 2 separate monitors, I realized
that it was really annoying to open up a ton of windows and resize them when it was always
just a few repeatable configurations.

### python mode
* editor for source code
* editor for tests
* browser for documentation/tickets
* terminal for arbitrary commands like linting and running tests

### web dev mode
* editor for source code
* editor for tests
* small terminal running linter
* small terminal using a filewatcher to run tests
* small terminal to automatically run typescript compiler
* medium terminal to run arbitrary commands

### documentation mode
* editor for document
* browser/pager for source material
* window that uses a filewatcher to autocompile the documentation

There were also a lot of consistent configurations that I wanted to use that just wouldn't
work out of the box. I like splitting my monitor up with 25-50-25 or 20-60-20 ratios and
that requires a lot of manual resizing. I could also set up elaborate rules in Sway and
then make sure each window fits into those rules, but I don't even know how that would work
since Sway can resize floating windows or existing windows, but an IDE that creates itself
in an instant wouldn't have any existing windows. And rules affect windows at window creation
so it's like a chicken-and-egg problem


Sure, I could just use `tmux`, but that came with some issues:
* tmux only handles terminals. it doesn't manage browsers, pdf viewers, or anything else
* tmux has its own keybindings. Even if I used `tmux` next to a browser, I'd be using different commands to jump between tmux and the windows. I can't do that! My brain is smol and it can't handle that complexity.

## Goals
* use only i3/sway to manage windows
* create a DIY IDE with a single command
* allow different IDEs to be defined through a readable file (like TOML)
* run arbitrary commands (not just shells and TUIs!)

## Defining an IDE in TOML
This toml config defines a complex IDE in a simple and consistent way. Read the [TOML spec](https://toml.io/en/v1.0.0#array-of-tables)
for more details on how to write a TOML file. I recommend drawing out the [i3 tree structure](https://i3wm.org/docs/userguide.html#_tree)
and then typing each node into a toml file as you do a [depth-first traversal](https://en.wikipedia.org/wiki/Depth-first_search).

This IDE divides the screen into 3 major sections with a 25-50-25 ratio. The middle and right sections each have
a terminal and the left section is split 60-40 into 2 terminals.

```toml
split = "horizontal"

[[screen]]
size = 25
split = "vertical"

[[screen.children]]
command = "alacritty --title medium-window"
size = 60

[[screen.children]]
command = "alacritty --title tiny-window"
size = 40

[[screen]]
command = "alacritty --title middle-panel"
size = 50

[[screen]]
command = "alacritty --title right-panel"
size = 25
```

[screenshot](screenshots/early_magic_tile.png)

## Shell Completion
[Setting up completion for your shell](completions)


## Alternatives
* [tmux](https://github.com/tmux/tmux)
