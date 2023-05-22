import asyncio, logging, os, sys
from functools import wraps
from pathlib import Path
from discord.ext import commands
from watchfiles import Change, awatch


logger = logging.getLogger('RebootRunner')
logger.addHandler(logging.NullHandler())
logger.propagate = False


class RebootRunner:
    def __init__(
        self,
        bot: 'Vile',
        path: str = 'cogs',
        debug: bool = True,
        loop: asyncio.BaseEventLoop = None,
        default_logger: bool = True,
        preload: bool = False,
        colors: bool = True,
    ):
        self.bot = bot
        self.path = path
        self.debug = debug
        self.loop = loop
        self.default_logger = default_logger
        self.preload = preload
        self.colors = colors

        if self.colors:
            self.CEND = '\33[0m'
            self.CBOLD = '\33[1m'
            self.CGREEN = '\33[32m'
            self.CRED = '\33[31m'
        else:
            self.CEND, self.CBOLD, self.CGREEN, self.CRED = '', '', '', ''

        if default_logger:
            watch_log = logging.getLogger('RebootRunner')
            watch_log.setLevel(logging.INFO)
            watch_handler = logging.StreamHandler(sys.stdout)
            watch_handler.setFormatter(logging.Formatter('[%(name)s] %(message)s'))
            watch_log.addHandler(watch_handler)


    @staticmethod
    def get_cog_name(path: str) -> str:
        _path = os.path.normpath(path)
        return _path.split(os.sep)[-1:][0][:-3]


    def get_dotted_cog_path(self, path: str) -> str:
        _path = os.path.normpath(path)
        tokens = _path.split(os.sep)
        reversed_tokens = list(reversed(tokens))

        try:
            root_index = reversed_tokens.index(self.path.split('/')[0]) + 1
        except ValueError:
            raise ValueError('Use forward-slash delimiter in your `path` parameter')

        return '.'.join([token for token in tokens[-root_index:-1]])


    async def _start(self):
        while self.dir_exists():
            try:
                async for changes in awatch(Path.cwd() / self.path):
                    self.validate_dir()

                    reverse_ordered_changes = sorted(changes, reverse=True)

                    for change in reverse_ordered_changes:
                        change_type = change[0]
                        change_path = change[1]

                        filename = self.get_cog_name(change_path)

                        new_dir = self.get_dotted_cog_path(change_path)
                        cog_dir = f'{new_dir}.{filename}' if new_dir else f'{self.path}.{filename}'

                        if change_type == Change.deleted:
                            if cog_dir in self.bot.extensions:
                                await self.unload(cog_dir)
                        elif change_type == Change.added:
                            if cog_dir not in self.bot.extensions:
                                await self.load(cog_dir)
                        elif change_type == Change.modified and change_type != (Change.added or Change.deleted):
                            if cog_dir in self.bot.extensions:
                                await self.reload(cog_dir)
                            else:
                                await self.load(cog_dir)

            except (FileNotFoundError, RuntimeError):
                continue

            else:
                await asyncio.sleep(1)

        else:
            await self.start()


    def check_debug(self):
        return any([(self.debug and __debug__), not self.debug])


    def dir_exists(self):
        return Path(Path.cwd() / self.path).exists()


    def validate_dir(self):
        if not self.dir_exists():
            raise FileNotFoundError
        return True


    async def start(self):
        _check = False
        while not self.dir_exists():
            if not _check:
                logger.error(f'The path {self.CBOLD}{Path.cwd() / self.path}{self.CEND} does not exist')
                _check = True

        else:
            logger.info(f'Found {self.CBOLD}{Path.cwd() / self.path}{self.CEND}!')
            if self.preload:
                await self._preload()

            if self.check_debug():
                if self.loop is None:
                    self.loop = asyncio.get_event_loop()

                logger.info(f'Watching for file changes in {self.CBOLD}{Path.cwd() / self.path}{self.CEND}')
                self.loop.create_task(self._start())


    async def load(self, cog_dir: str):
        try:
            await self.bot.load_extension(cog_dir)
        except commands.ExtensionAlreadyLoaded:
            logger.info(f"Cannot load {cog_dir}; it isn't loaded")
        except commands.NoEntryPointError:
            logger.info(
                f'{self.CBOLD}{self.CRED}[Error]{self.CEND} Failed to load {self.CBOLD}{cog_dir}{self.CEND}; no entry point found'
            )
        except Exception as exc:
            self.cog_error(exc)
        else:
            logger.info(f'{self.CBOLD}{self.CGREEN}[Cog Loaded]{self.CEND} {cog_dir}')


    async def unload(self, cog_dir: str):
        try:
            await self.bot.unload_extension(cog_dir)
        except commands.ExtensionNotLoaded:
            logger.info(f"Cannot unload {cog_dir}; it isn't loaded")
        except Exception as exc:
            self.cog_error(exc)
        else:
            logger.info(f'{self.CBOLD}{self.CRED}[Cog Unloaded]{self.CEND} {cog_dir}')


    async def reload(self, cog_dir: str):
        try:
            await self.bot.reload_extension(cog_dir)
        except commands.NoEntryPointError:
            logger.info(
                f'{self.CBOLD}{self.CRED}[Error]{self.CEND} Failed to reload {self.CBOLD}{cog_dir}{self.CEND}; no entry point found'
            )
        except commands.ExtensionNotLoaded:
            logger.info(f"Cannot reload {cog_dir}; it isn't loaded")
        except Exception as exc:
            self.cog_error(exc)
        else:
            logger.info(f'{self.CBOLD}{self.CGREEN}[Cog Reloaded]{self.CEND} {cog_dir}')


    @staticmethod
    def cog_error(exc: Exception):
        if isinstance(exc, (commands.ExtensionError, SyntaxError)):
            logging.exception(exc)


    async def _preload(self):
        logger.info('Preloading cogs')
        for cog in {(file.stem, file) for file in Path(Path.cwd() / self.path).rglob('*.py')}:
            new_dir = self.get_dotted_cog_path(cog[1])
            await self.load('.'.join([new_dir, cog[0]]))


def watch(**kwargs):
    def decorator(function):
        @wraps(function)
        async def wrapper(client):
            cw = Watcher(client, **kwargs)
            await cw.start()
            ret_val = await function(client)
            return ret_val

        return wrapper

    return decorator