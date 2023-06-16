from importlib import import_module, reload
from pathlib import Path

from .memory import *
from .network import *

for patch in Path("helpers/managers/patch").glob("**/*.py"):
    reload(import_module(f"helpers.managers.patch.{patch.stem}"))
