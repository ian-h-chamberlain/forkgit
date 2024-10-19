import sys

from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType


git_exe_dir = Path(sys.executable).parent
loader = SourceFileLoader('git', git_exe_dir / 'git.py')
mod = ModuleType(loader.name)
loader.exec_module(mod)
mod.main()
