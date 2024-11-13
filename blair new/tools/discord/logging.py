from logging import INFO, basicConfig, getLogger

ignore = ("pomice", "client", "pyppeteer")
for module in ignore:
    logger = getLogger(module)
    logger.disabled = True
    logger.propagate = False

basicConfig(
    level=INFO,
    format="\x1b[35m{process}\x1b[0m: \x1b[33m{levelname:<9}\x1b[0m | \x1b[36m{asctime}\x1b[0m | @ \x1b[31m{module:<9} -> \x1b[0m{message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)
