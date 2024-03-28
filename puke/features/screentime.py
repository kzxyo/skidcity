from __future__ import annotations
import asyncio
import os
import plotly.express as px
from puke.managers import Context
from puke import Puke
from discord.ext.commands import Cog
from typing import Final, Literal, Optional, List
from discord import Member, Guild, Embed, User, File
from discord.ext.commands import group, command, Author, cooldown, BucketType
from time import mktime
from datetime import datetime, timedelta
if not os.path.exists('./data/new_status'):
    os.makedirs('./data/new_status')


def Percent(first: int, second: int, integer: bool = False) -> float | int:
    percentage = (first / second * 100)
    if integer is True:
        return round(float(percentage), 2)
    return percentage


def GenerateChart(data: List, member: Member):
    days: Final = Literal[30, 13, 6, 0] == 31

    dataset = [i for i in data if (datetime.now() - datetime.fromisoformat(i[5])).days <= days]
    online = round(sum([i[1] for i in dataset])/60/60, 2)
    idle = round(sum([i[2] for i in dataset])/60/60, 2)
    dnd = round(sum([i[3] for i in dataset])/60/60, 2)
    offline = round(sum([i[4] for i in dataset])/60/60, 2)
    dataset = [dataset[0][0], online, idle, dnd, offline, dataset[0][5]]

    total_ = sum(dataset[1:5])

    names  = [f'Online<br>{online} Hours<br>{Percent(dataset[1], total_, True)}%',
                f'Idle<br>{idle} Hours<br>{Percent(dataset[2], total_, True)}%',
                f'DND<br>{dnd} Hours<br>{Percent(dataset[3], total_, True)}%',
                f'Offline<br>{offline} Hours<br>{Percent(dataset[4], total_, True)}%']
    
    px.defaults.width = 829
    px.defaults.height = 625

    figure = px.pie(
        values = dataset[1:5],
        hole = 0.60,
        names = names,
        color = names,
        color_discrete_map={
            names[0]: '#43b581',
            names[1]: '#faa61a',
            names[2]: '#f04747',
            names[3]: '#747f8d'
            
        },
    )

    figure.update_traces(textinfo='none')
    figure.update_layout(paper_bgcolor='rgba(0,0,255,0)', legend_font_color='#FFFFFF', legend_font_size=24, legend_tracegroupgap=15)
    file = f"{str(member)}-{int(mktime(datetime.now().timetuple()) * 1000)}.png"
    figure.write_image(f'./data/new_status/{file}')
    return file


class Screentime(Cog):
    def __init__(self, bot: Puke):
        self.bot: Puke = bot

    @Cog.listener(name='on_member_update')
    async def screentime_member_update(self: "Screentime", before: Member, after: Member):
        if before.bot or not before.guild or before == self.bot.user:
            return
        if before.status != after.status:
            now = datetime.now()
            await self.bot.db.execute(
                """
                INSERT INTO screentime (user_id, online, idle, dnd, offline, time) VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (user_id) DO NOTHING
                """,
                after.id, 0, 0, 0, 0, str(now)
            )
            DATASET = [
                i for i in await self.bot.db.fetch(
                    "SELECT * FROM screentime WHERE user_id = $1",
                    before.id
                ) if (datetime.now() - datetime.fromisoformat(i[5])).days <= 30
            ]
            try:
                sort = sorted(
                    map(
                        list, DATASET
                    ),
                    key=lambda x: datetime.fromisoformat(x[5]),
                    reverse=True
                )[0]
            except:
                raise

            online, idle, dnd, offline = 0, 0, 0, 0
            status = before.status.name
            time = datetime.fromisoformat(sort[5])
            new_time: timedelta = (now - time)

            if status == 'online':
                online += new_time.seconds

            elif status == 'idle':
                idle += new_time.seconds
            
            elif status == 'dnd':
                dnd += new_time.seconds
            
            elif status == 'offline':
                offline += new_time.seconds
            
            if any([online, idle, dnd, offline]):
                await self.bot.db.execute(
                    """
                    INSERT INTO screentime (user_id, online, idle, dnd, offline, time) VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (user_id) DO UPDATE SET online = screentime.online + $2, idle = screentime.idle + $3, dnd = screentime.dnd + $4, offline = screentime.offline + $5, time = $6
                    """,
                    before.id, online, idle, dnd, offline, str(now)
                )

    @Cog.listener(name='on_presence_update')
    async def screentime_presence_update(self: "Screentime", before: User, after: User):
        if before.bot or not before.guild or before == self.bot.user:
            return

        if before.status != after.status:
            now = datetime.now()
            await self.bot.db.execute(
                """
                INSERT INTO screentime (user_id, online, idle, dnd, offline, time) VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (user_id) DO NOTHING
                """,
                after.id, 0, 0, 0, 0, str(now)
            )
            DATASET = [
                i for i in await self.bot.db.fetch(
                    "SELECT * FROM screentime WHERE user_id = $1",
                    before.id
                ) if (datetime.now() - datetime.fromisoformat(i[5])).days <= 30
            ]
            try:
                sort = sorted(
                    map(
                        list, DATASET
                    ),
                    key=lambda x: datetime.fromisoformat(x[5]),
                    reverse=True
                )[0]
            except:
                raise

            online, idle, dnd, offline = 0, 0, 0, 0
            status = before.status.name
            time = datetime.fromisoformat(sort[5])
            new_time: timedelta = (now - time)

            if status == 'online':
                online += new_time.seconds

            elif status == 'idle':
                idle += new_time.seconds
            
            elif status == 'dnd':
                dnd += new_time.seconds
            
            elif status == 'offline':
                offline += new_time.seconds
            
            if any([online, idle, dnd, offline]):
                await self.bot.db.execute(
                    """
                    INSERT INTO screentime (user_id, online, idle, dnd, offline, time) VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (user_id) DO UPDATE SET online = screentime.online + $2, idle = screentime.idle + $3, dnd = screentime.dnd + $4, offline = screentime.offline + $5, time = $6
                    """,
                    before.id, online, idle, dnd, offline, str(now)
                )


    @command(name='screentime', aliases=['st', 'screen'], brief='Shows screentime of a member')
    async def screentime(self: "Screentime", ctx: Context, member: Member | User = Author):
        async with ctx.typing():
            data = await self.bot.db.fetch(
                """
                SELECT * FROM screentime WHERE user_id = $1
                """,
                member.id
            )
            if not data:
                return await ctx.warn("No data found for this member")

            now = datetime.now()
            DATASET = [
                i for i in data if (now - datetime.fromisoformat(i[5])).days <= 30
            ]
            munch = sorted(
                map(list, DATASET),
                key=lambda x: datetime.fromisoformat(x[5]),
                reverse=True
            )
            online = round(sum([i[1] for i in munch])/60/60, 2)
            idle = round(sum([i[2] for i in munch])/60/60, 2)
            dnd = round(sum([i[3] for i in munch])/60/60, 2)
            offline = round(sum([i[4] for i in munch])/60/60, 2)

            if not any([online, idle, dnd, offline]):
                return await ctx.warn("No data **found** for this member")
            
            chart = await self.bot.loop.run_in_executor(None, GenerateChart, data, member)
            
            file = File(f'./data/new_status/{chart}', filename="pie.png")

            await ctx.reply(files=[file])

            try:
                await asyncio.sleep(4)
                os.remove(f'./data/new_status/{chart}')
            except:
                raise

    
async def setup(bot):
    await bot.add_cog(Screentime(bot))