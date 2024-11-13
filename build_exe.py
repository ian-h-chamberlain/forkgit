#!/usr/bin/env python3

"""
Build an exe wrapper using the current python interpreter. Unlike e.g. pyinstaller,
this is just a simple shim to launch bin/git.py and does not bundle an interpreter,
which also makes it somewhat faster to launch vs a pyinstaller executable.

Requires distlib, which can be installed with pip, or may already be installed
in your environment.
"""

from distlib.scripts import ScriptMaker
import pathlib
import os
import textwrap


class Builder(ScriptMaker):
    """
    References:
    - https://stackoverflow.com/a/76371853
    - https://distlib.readthedocs.io/en/latest/reference.html#the-distlib-scripts-package
    """

    def __init__(self, directory: os.PathLike):
        super().__init__(str(directory), str(directory), add_launchers=True)

        self.variants = [""]
        self.script_template = self.script_template.replace(
            "import sys",
            textwrap.dedent(
                r"""
                import sys
                import os
                # Allow imports from siblings of the .exe file. In this case,
                # __file__ looks something like "...\git.exe\__main__.py"
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            """,
            ),
        )


if __name__ == "__main__":
    bin_dir = pathlib.Path(__file__).parent / "bin"
    Builder(bin_dir).make_multiple(
        # Spec is similar to e.g. setup.cfg
        [
            "git = git:main",
            "sh = git:sh",
            "bash = git:bash",
        ],
        options={"gui": False},
    )
