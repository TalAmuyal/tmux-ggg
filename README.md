Tmux ggg is a tmux session manager that allows you to easily start new tmux sessions using a simple command-line interface.

# Installation

```bash
uv tool install tmux-ggg
```

# Usage

```bash
ggg add -w ~/workspace # Register a directory for ggg to look for projects
ggg add -p ~/.local/my-project # Register a directory of a specific project

ggg # Open a list of inactive projects to start a new tmux session and attach to it
```


# Development

TBD.


# License

This project is licensed under the MIT license (https://choosealicense.com/licenses/mit/).
See the `LICENSE.txt` file for more information.
