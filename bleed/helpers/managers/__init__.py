from importlib import import_module, reload
from pathlib import Path

from .context import *
from .memory import *
from .network import *
from .ratelimit import *


for patch in Path("helpers/managers/patch").glob("**/*.py"):
    reload(import_module(f"helpers.managers.patch.{patch.stem}"))
