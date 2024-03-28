from logging import INFO, basicConfig, getLogger

g = "\033[92m"
r = "\033[0m"

basicConfig(
    level=INFO,
    format=f"{g}[dev/{{module}}]{r} {{message}}",
    datefmt=None,
    style="{",
)