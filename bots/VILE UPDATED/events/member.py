import discord, arrow
from datetime import datetime
from utilities import utils
from utilities.baseclass import Vile
from discord.ext import commands


class MemberEvents(commands.Cog):
    def __init__(self, bot: Vile):
        self.bot = bot


    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):

        # booster roles
        if (
            (before.premium_since != None and after.premium_since is None)
            or (before.guild.premium_subscriber_role in before.roles and after.guild.premium_subscriber_role not in after.roles)
        ):
            booster_role = await self.bot.db.fetchval('SELECT role_id FROM boosterrole_roles WHERE guild_id = %s AND user_id = %s', before.guild.id, before.id)
            if booster_role:
                if before.guild.get_role(booster_role):
                    await before.guild.get_role(booster_role).delete(reason='booster role deleted; no longer boosting')

        # my nickname
        if after.id == self.bot.user.id and after.guild.owner_id != self.bot.owner.id:
            if after.nick:
                try:
                    await after.edit(nick=None)
                except:
                    pass

    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if member.bot: 
            return

        if self.bot.cache.antiraid.get(member.guild.id) is not None and member.id not in self.bot.cache.antiraid_whitelist.get(member.guild.id, list()):
            if member.guild.id not in self.bot.cache.antiraid_trigger:
                self.bot.cache.antiraid_trigger[member.guild.id] = 0
                
            self.bot.cache.antiraid_trigger[member.guild.id] += 1

            # if self.bot.cache.antiraid_trigger[member.guild.id] >= self.bot.cache.antiraid[member.guild.id]['joins']:
            #     try:
            #         await member.guild.edit(invites_disabled=True, reason='vile antiraid: join threshold exceeded')
            #     except:
            #         pass

            if self.bot.cache.antiraid[member.guild.id]['avatar'] == True and member.avatar is None:
                try:
                    await member.kick(reason='vile antiraid: user has no avatar')
                except:
                    pass

            if self.bot.cache.antiraid[member.guild.id]['age'] > (datetime.now().astimezone() - member.created_at).days:
                try:
                    await member.kick(reason='vile antiraid: user is too young')
                except:
                    pass


        if self.bot.cache.welcomechannel.get(member.guild.id) is not None:
            if self.bot.cache.welcomemessage.get(member.guild.id) is not None:
                channel = self.bot.cache.welcomechannel[member.guild.id]
                msg = self.bot.cache.welcomemessage[member.guild.id]
                
                if member.guild.get_channel(channel):
                    await member.guild.get_channel(channel).send(
                        **await utils.to_object(await utils.embed_replacement(member, msg))
                    )
        
        if self.bot.cache.joindm.get(member.guild.id) is not None:
            if 15 >= self.bot.cache.limits['dms'].get(member.guild.id, 0):
                msg = self.bot.cache.joindm[member.guild.id]

                if member.dm_channel.permissions_for(self.bot.user).send_messages is True:
                    await member.send(
                        **await utils.to_object(await utils.embed_replacement(member, msg))
                    )
                if member.guild.id not in self.bot.cache.limits['dms']:
                    self.bot.cache.limits['dms'][member.guild.id] = 0
                self.bot.cache.limits['dms'][member.guild.id] += 1

        if self.bot.cache.autoroles.get(member.guild.id) is not None:
            for role in self.bot.cache.autoroles[member.guild.id]:
                role = member.guild.get_role(role)
                if role:
                    if role.is_assignable():
                        await member.add_roles(role, reason='autorole')

        if self.bot.cache.discriminator_roles.get(member.guild.id) is not None:
            for entry in utils.filter(self.bot.cache.discriminator_roles[member.guild.id], key=lambda d: d['discriminator'] == member.discriminator):
                role = member.guild.get_role(entry['role_id'])
                if role:
                    if role.is_assignable():
                        await member.add_roles(role, reason=f'vile discriminator: member has the {member.discriminator} discriminator')

        if self.bot.cache.pingonjoin.get(member.guild.id) is not None:
            channels = self.bot.cache.pingonjoin[member.guild.id]
            
            for channel in channels:
                if member.guild.get_channel(channel):
                    await member.guild.get_channel(channel).send(member.mention, delete_after=0)


    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        if member.bot: 
            return

        if self.bot.cache.goodbyechannel.get(member.guild.id) is not None:
            if self.bot.cache.goodbyemessage.get(member.guild.id) is not None:
                channel = self.bot.cache.goodbyechannel[member.guild.id]
                msg = self.bot.cache.goodbyemessage[member.guild.id]
                
                if member.guild.get_channel(channel):
                    await member.guild.get_channel(channel).send(
                        **await utils.to_object(await utils.embed_replacement(member, msg))
                    )


async def setup(bot: Vile):
    await bot.add_cog(MemberEvents(bot))
