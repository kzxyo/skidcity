from pathlib import Path
from importlib import import_module, reload

for patch in Path("helpers/patch").glob("**/*.py"):
    reload(import_module(f"helpers.patch.{patch.stem}"))
