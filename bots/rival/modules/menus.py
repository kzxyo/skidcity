import discord
from discord.ext import menus
from discord.ext.menus.views import ViewMenu, ViewMenuPages


class Menu(ViewMenuPages):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ListMenu(menus.ListPageSource):
    def __init__(self, data, per_page=20, embed=None):
        if embed is None:
            self.embed = discord.Embed()
        else:
            self.embed = embed

        super().__init__(data, per_page=per_page)

        if self.is_paginating():
            if self.embed.footer.text is not None:
                self.og_footer = " | " + self.embed.footer.text
            else:
                self.og_footer = ""

    async def format_page(self, menu, entries):
        self.embed.description = "\n".join(entries)
        if self.is_paginating():
            footer_text = f"{menu.current_page+1}/{self.get_max_pages()}{self.og_footer}"
            self.embed.set_footer(text=footer_text)
        return self.embed


class Confirm(ViewMenu):
    def __init__(self, msg):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.msg = msg
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await self.send_with_view(channel, self.msg)

    @menus.button("\N{WHITE HEAVY CHECK MARK}")
    async def do_confirm(self, payload):
        self.result = True
        self.stop()

    @menus.button("\N{CROSS MARK}")
    async def do_deny(self, payload):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.result