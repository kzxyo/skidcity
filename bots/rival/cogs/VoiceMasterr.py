from http import client
import discord,datetime, asyncio
from discord.ext import commands
from modules import util,Message,exceptions,consts
MISSING = discord.utils.MISSING
lock="<:lock:1021614489294090240>"
unlock="<:unlock:1021287647206969405>"
ghost="<:ghost:1021615473470734356>"
unghost="<:unghost:1021615709438095371>"
claim="<:user:1021271042808872990>"
delete="<:trash:1021287734356213780>"
transfer="<:crown:1021288068730327070>"
permit="<:plus:1021287916951056404>"
unpermit="<:minus:1021287996571529226>"
rename="<:channel:1021287829826981939>"
class RenameInput(discord.ui.Modal, title='VoiceMaster Channel Rename'):
    def __init__(self, bot):
        super().__init__()
        self.bot=bot

    renamee = discord.ui.TextInput(label='rename', placeholder="what would you like to name it?")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        data = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if data:
            try:
                channel = self.bot.get_channel(data)
            except:
                channel = await self.bot.fetch_channel(data)
            await channel.edit(name=self.renamee.value)
            return await interaction.response.send_message(f"{interaction.user} your channel name has been set to `{self.renamee.value}`", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)
        
class MemberInput(discord.ui.Modal, title='VoiceMaster Input Member'):
    def __init__(self, bot):
        super().__init__()
        self.bot=bot
    
    name = discord.ui.TextInput(
        label='Discord name & tag', 
        placeholder='EX: cop#0001...',
    )
    async def on_submit(self, interaction:discord.Interaction) -> None:
        check2 = await self.bot.db.execute("""SELECT owner_id FROM vm_data WHERE channel_id = %s""", interaction.user.voice.channel.id, one_value=True)
        if check2:
            ya=self.name.value.split("#")
            name=ya[0]
            tag=ya[1]
            member=discord.utils.get(interaction.guild.members,name=name,discriminator=tag)
            if member:
                await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", interaction.user.voice.channel.id)
                await self.bot.db.execute("""INSERT INTO vm_data VALUES(%s, %s, %s, %s)""", interaction.user.voice.channel.id, interaction.guild.id, member.id, member.id)
                return await interaction.response.send_message(f"{interaction.user} your channel's ownership has been transferred to {member.mention}", ephemeral=True)
            else:
                return await interaction.response.send_message(f"{interaction.user} no member found named {self.name.value}", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

class PermitInput(discord.ui.Modal, title='VoiceMaster Permit Member'):
    def __init__(self, bot):
        super().__init__()
        self.bot=bot
    
    name = discord.ui.TextInput(
        label='Discord name & tag', 
        placeholder='EX: cop#0001...',
    )
    async def on_submit(self, interaction:discord.Interaction) -> None:
        check2 = await self.bot.db.execute("""SELECT owner_id FROM vm_data WHERE channel_id = %s""", interaction.user.voice.channel.id, one_value=True)
        if check2:
            ya=self.name.value.split("#")
            name=ya[0]
            tag=ya[1]
            member=discord.utils.get(interaction.guild.members,name=name,discriminator=tag)
            if member:
                await interaction.user.voice.channel.set_permissions(member, connect=True)
                return await interaction.response.send_message(f"{interaction.user} {member.mention} can now join", ephemeral=True)
            else:
                return await interaction.response.send_message(f"{interaction.user} no member found named {self.name.value}", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

class UNPermitInput(discord.ui.Modal, title='VoiceMaster UNPermit Member'):
    def __init__(self, bot):
        super().__init__()
        self.bot=bot
    
    name = discord.ui.TextInput(
        label='Discord name & tag', 
        placeholder='EX: cop#0001...',
    )
    async def on_submit(self, interaction:discord.Interaction) -> None:
        check2 = await self.bot.db.execute("""SELECT owner_id FROM vm_data WHERE channel_id = %s""", interaction.user.voice.channel.id, one_value=True)
        if check2:
            ya=self.name.value.split("#")
            name=ya[0]
            tag=ya[1]
            member=discord.utils.get(interaction.guild.members,name=name,discriminator=tag)
            if member:
                await interaction.user.voice.channel.set_permissions(member, connect=False)
                if member in interaction.user.voice.channel.members:
                    await member.edit(voice_channel=None)
                return await interaction.response.send_message(f"{interaction.user} {member.mention} can no longer join", ephemeral=True)
            else:
                return await interaction.response.send_message(f"{interaction.user} no member found named {self.name.value}", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

class PersistentView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = 0
        self.bot = bot

       # url = f'https://discord.com/api/oauth2/authorize?client_id=776128410547126322&permissions=8&scope=bot'

    @discord.ui.button(emoji=lock, custom_id="Lock_Button",style=discord.ButtonStyle.grey)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            data = find
            try:
                channel = self.bot.get_channel(data)
                await channel.set_permissions(interaction.guild.default_role, connect=False)
            except:
                channel=await self.bot.fetch_channel(data)
                await channel.set_permissions(interaction.guild.default_role, connect=False)
            return await interaction.response.send_message(f"{interaction.user} your channel has been locked", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)
   
    @discord.ui.button(emoji=unlock, custom_id="Unlock_Button",style=discord.ButtonStyle.grey)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        print(find)
        if find:
            data = find
            try:
                channel = await self.bot.get_channel(data)
                await channel.set_permissions(interaction.guild.default_role, connect=True)
            except:
                channel=await self.bot.fetch_channel(data)
                await channel.set_permissions(interaction.guild.default_role, connect=True)
            return await interaction.response.send_message(f"{interaction.user} your channel has been unlocked", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)
   
    @discord.ui.button(emoji=ghost, custom_id="Ghost_Button",style=discord.ButtonStyle.grey)
    async def ghost(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            data = find
            try:
                channel = self.bot.get_channel(data)
                await channel.set_permissions(interaction.guild.default_role, view_channel=False)
            except:
                channel=await self.bot.fetch_channel(data)
                await channel.set_permissions(interaction.guild.default_role, view_channel=False)
            return await interaction.response.send_message(f"{interaction.user} your channel has been ghosted", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

    @discord.ui.button(emoji=unghost, custom_id="Unghost_Button",style=discord.ButtonStyle.grey)
    async def unghost(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            data = find
            try:
                channel = self.bot.get_channel(data)
                await channel.set_permissions(interaction.guild.default_role, view_channel=True)
            except:
                channel=await self.bot.fetch_channel(data)
                await channel.set_permissions(interaction.guild.default_role, view_channel=True)
            return await interaction.response.send_message(f"{interaction.user} your channel has been unghosted", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

    @discord.ui.button(emoji=claim, custom_id="Claim_Button",style=discord.ButtonStyle.grey)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.voice:
                check2 = await self.bot.db.execute("""SELECT owner_id FROM vm_data WHERE channel_id = %s""", interaction.user.voice.channel.id, one_value=True)
                owner=interaction.guild.get_member(check2)
                if not await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", interaction.user.voice.channel.id):
                    return await interaction.response.send_message(f"this channel is not a voicemaster channel", ephemeral=True)
                if owner in interaction.user.voice.channel.members:
                    return await interaction.response.send_message(f"the owner is still in the voice channel", ephemeral=True)
                else:
                    c=interaction.user.voice.channel
                    try:
                        owner=interaction.guild.get_member(await self.bot.db.execute("""SELECT owner_id FROM vm_data WHERE channel_id = %s""", c.id, one_value=True))
                    except:
                        owner=await self.bot.fetch_user(check2)
                    if interaction.user.voice.channel.name == f"{owner.name}'s channel":
                        await c.edit(name=f"{interaction.user.name}'s channel")
                    await self.bot.db.execute("""INSERT INTO vm_data VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE owner_id = VALUES(owner_id)""", interaction.user.voice.channel.id, interaction.guild.id, interaction.user.id, interaction.user.id)
                    return await interaction.response.send_message(f"you are now the channel owner", ephemeral=True)
            else:
                return await interaction.response.send_message("You're not connected to **a** voice channel", ephemeral=True)
        except Exception as e:
            print(e)
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

    @discord.ui.button(emoji=permit, custom_id="Permit_Button",style=discord.ButtonStyle.grey)
    async def Permit(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            data = find
            await interaction.response.send_modal(PermitInput(self.bot))
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)


    @discord.ui.button(emoji=unpermit, custom_id="UNPermit_Button",style=discord.ButtonStyle.grey)
    async def UnPermit(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            data = find
            await interaction.response.send_modal(UNPermitInput(self.bot))
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

    @discord.ui.button(emoji=rename, custom_id="Rename_Button",style=discord.ButtonStyle.grey)
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            data = find
            try:
                await interaction.response.send_modal(RenameInput(self.bot))
            except:
                await interaction.response.send_modal(RenameInput(self.bot))
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

    @discord.ui.button(emoji=transfer, custom_id="Transfer_Button",style=discord.ButtonStyle.grey)
    async def transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            data = find
            try:
                await interaction.response.send_modal(MemberInput(self.bot))
            except:
                await interaction.response.send_modal(MemberInput(self.bot))
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)

    @discord.ui.button(emoji=delete, custom_id="Delete_Button", style=discord.ButtonStyle.grey)
    async def delete(self, interaction:discord.Interaction, button: discord.ui.Button):
        find = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s and guild_id = %s""", interaction.user.id, interaction.guild.id, one_value=True)
        if find:
            try:
                channel=self.bot.get_channel(find)
            except:
                channel=await self.bot.fetch_channel(find)
            await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", channel.id)
            await channel.delete()
            return await interaction.response.send_message("Deleted **your** voice channel", ephemeral=True)
        else:
            return await interaction.response.send_message("You're not connected to **your** voice channel", ephemeral=True)


class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__()
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(PersistentView())
            self.persistent_views_added = True
 
class VoiceMasterr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color=self.bot.color
        self.em=consts

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", channel.id):
            await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""",channel.id)

    @commands.command(name='claim', description="claim roles in rival support")
    async def claim(self, ctx, code=None):
        if code:
            if await self.bot.db.execute("""SELECT * from codes WHERE code = %s""", code):
                await self.bot.db.execute("""DELETE FROM codes WHERE code = %s""", code)
                await util.send_good(ctx, f"successfully redeemed donator from code `{code}`")
                c=self.bot.get_channel(1013599556384067594)
                await c.send(embed=discord.Embed(color=self.color, description=f"**{ctx.author}** redeemed `{code}`").set_footer(text=f"ID: {ctx.author.id}"))
                return await self.bot.db.execute("INSERT INTO dnr (user_id, ts) VALUES (%s, %s)",ctx.author.id,datetime.datetime.now(),)
            else:
                return await util.send_bad(ctx, f"no promo code found under `{code}`")
        if ctx.guild.id != 918445509599977472:
            return await util.send_error(ctx, f"only available in `rival support`")
        c=0
        ls=[guild for guild in self.bot.guilds if guild.owner.id == ctx.author.id and len(guild.members) >= 1000]
        if len(ls) == 0:
            return await util.send_error(ctx, "no guilds found with your ownership with over 1000 members")
        members=[len(guild.members) for guild in self.bot.guilds if guild.owner.id == ctx.author.id]
        for guild in self.bot.guilds:
            if guild.owner.id == ctx.author.id:
                if len(guild.members) > 10000:
                    await ctx.author.add_roles(ctx.guild.get_role(1013294740978008104))
                if len(guild.members) > 5000:
                    await ctx.author.add_roles(ctx.guild.get_role(1013294785676718090))
                if len(guild.members) > 1000:
                    await ctx.author.add_roles(ctx.guild.get_role(1013294807453540423))
                if len(guild.members) >= 25000:
                    await ctx.author.add_roles(ctx.guild.get_role(1015363827266748466)) 
                if len(guild.members) >= 50000:
                    await ctx.author.add_roles(ctx.guild.get_role(1015363860317863987)) 
                if len(guild.members) >= 75000:
                    await ctx.author.add_roles(ctx.guild.get_role(1015377093196009594))
                if len(guild.members) >= 100000:
                    await ctx.author.add_roles(ctx.guild.get_role(1015363883592061009))
        if len(members) < 1000:
            return await util.send_error(ctx, "no guilds found with your ownership with over `1,000 members`")
        else:
            await util.send_good(ctx, f"claimed roles for providing rival with `{len(members)}` members and `{len(ls)}` guilds")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if after.channel:
                if before.channel:
                    if after.channel.id == before.channel.id:
                        return
                if await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", after.channel.id):
                    if after.channel.guild.id in self.bot.cache.adminlock:
                        if after.channel.permissions_for(after.channel.guild.default_role).connect == False:
                            if member not in after.channel.overwrites and member.id != member.guild.owner.id:
                                if not after.channel.overwrites_for(member).connect == True:
                                    try:
                                        await member.edit(voice_channel=None)
                                    except Exception as e:
                                        #print(e)
                                        pass
                                    if len(before.channel.members) == 1:
                                        if await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", before.channel.id):
                                            await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", before.channel.id)
                                            await before.channel.delete() 
                                    return 
        except:
            pass
        try:
            if before.channel and await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", before.channel.id):
                if not after.channel:
                    chh=before.channel.guild.get_channel(before.channel.id)
                    if chh:
                        if len(chh.members) == 0:
                            await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", before.channel.id)
                            await before.channel.delete() 
            if before.channel:
                mc=[member for member in before.channel.members if not member.bot]
                if not after.channel:
                    if len(mc) == 1 and await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", before.channel.id):
                        await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", before.channel.id)
                        await before.channel.delete() 
            if before.channel:
                if len(before.channel.members) == 1 and not after.channel.members and await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", before.channel.id):
                    await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", before.channel.id)
                    await before.channel.delete()
            if before.channel:
                if len(before.channel.members) == 0 and await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", before.channel.id):
                    await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", before.channel.id)
                    await before.channel.delete()
            if after.channel:
                if len(after.channel.members) == 0 and await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", after.channel.id):
                    await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", before.channel.id)
                    await before.channel.delete()
            if after.channel:
                if len(after.channel.members) == 1 and after.channel.members[0].bot and await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s""", before.channel.id):
                    await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", before.channel.id)
                    await before.channel.delete()
            if before.channel and after.channel:
                if before.channel.id == after.channel.id:
                    return
            if not after.channel:
                return
        except Exception as e:
            print(e)
        try:
            guildID = member.guild.id
            check = await self.bot.db.execute("""SELECT category,channel FROM guild_vm WHERE guild_id = %s""", member.guild.id)
            if check:
                for category, channel in check:
                    category=category
                    channel=channel
            if check:
                if not await self.bot.db.execute("""SELECT * FROM vm_data WHERE user_id = %s AND guild_id = %s AND owner_id = %s""", member.id, member.guild.id, member.id):
                    pass
                else:
                    try:
                        if after.channel.id == channel:
                            return await member.send(embed=discord.Embed(description="**you have to many voice channels currently, you can transfer ownership by using !vm transfer to transfer to another member**", color=self.color))
                    except:
                        return
                if after.channel.id == channel:
                    category=category
                    category2 = self.bot.get_channel(category)
                    name = f"{member.name}'s channel"
                    channel2 = await member.guild.create_voice_channel(name, category=category2, bitrate=int(member.guild.bitrate_limit))
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                    await asyncio.sleep(1)
                    await self.bot.db.execute("""INSERT INTO vm_data VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE guild_id = VALUES(guild_id) AND user_id = VALUES(user_id) AND owner_id = VALUES(owner_id)""", channel2.id, member.guild.id, member.id, member.id)
                    def check(a,b,c):
                        mc=[member for member in channel2.members if not member.bot]
                        return len(mc) == 0
                    await self.bot.wait_for('voice_state_update', check=check)
                    await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", channel2.id)
                    await channel2.delete(reason="Voice channel was left empty")
                    await asyncio.sleep(3)
            else:
                return
        except Exception as e:
            return

    @commands.group(aliases = ['voicemaster', 'vm', 'vc'],description = "Create your own custom/temporary voice channels through the bot",brief = "subcommand",help = "```Syntax: !voicemaster [subcommand]\nExample: !voicemaster setup```")
    async def voice(self, ctx):
        if ctx.invoked_subcommand is None:
            return await util.command_group_help(ctx)

    @voice.command(name='interface', description="sends the voice master interface")
    async def voice_interface(self, ctx):
        embed = discord.Embed(title="Rival Interface", description="Click the buttons below to control your voice channel   \u200b", url="https://rival.rocks/discord", color=self.bot.color).add_field(name="Button Usage", inline=True, value=f"{lock} ・ [`Lock`](https://discord.gg/rivalbot) the voice channel\n{unlock} ・ [`Unlock`](https://discord.gg/rivalbot) the voice channel\n{ghost} ・ [`Ghost`](https://discord.gg/rivalbot) the voice channel\n{unghost} ・ [`Reveal`](https://discord.gg/rivalbot) the voice channel\n{claim} ・ [`Claim`](https://discord.gg/rivalbot) the voice channel\n{permit} ・ [`Permit`](https://discord.gg/rivalbot) a member\n{unpermit} ・ [`Reject`](https://discord.gg/rivalbot) a member\n{rename} ・ [`Rename`](https://discord.gg/rivalbot) the channel\n{transfer} ・ [`Transfer`](https://discord.gg/rivalbot) channel ownership\n{delete} ・ [`Delete`](https://discord.gg/rivalbot) the channel")
      #  embed.add_field(name="<:lock:1009263067193942117> Lock", value="Lock's your channel so that other members cannot join it.", inline=False)
       # embed.add_field(name="<:unlock2:1009376645125259284> Unlock", value="Unlock's your channel so others may join it.", inline=False)
       # embed.add_field(name="<:ghost:1009227118942634084> Ghost", value="Make your channel invisible", inline=False)
       # embed.add_field(name="<:unghost:1009227230490132580> UnGhost", value="Make your channel visible", inline=False)
      #  embed.add_field(name="<a:aw_whiteuser:1009275774668390492> Claim", value = "Claim ownership of the channel after the owner leaves", inline=False)
        #embed.add_field(name="<:trash:1005550877861494814> Delete", value="Delete your channel.", inline=False)
        embed.set_footer(text="The Rival Team", icon_url="https://rival.rocks/invite")
        await ctx.send(embed=embed, view=PersistentView(self.bot))

    @voice.command(name='setup',description="Setup the voicemaster module ",aliases=['enable', 'on','true'],brief="category", extras={'perms':"Manage_Channels"}, usage="```Swift\nSyntax: !vm setup <category>\nExample: !vm setup rival```")
    @commands.has_permissions(manage_channels=True)
    async def voice_setup(self, ctx, category:discord.CategoryChannel=None):
        guildID = ctx.guild.id
        check = await self.bot.db.execute("""SELECT category,channel FROM guild_vm WHERE guild_id = %s""", guildID)
        if not check:
            guildID = ctx.guild.id
            id = ctx.author.id
            embed = discord.Embed(description=f"{self.em.warn} Please wait while I set this up!", color=self.em.error)
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(1)
            if category is None:
                new_cat = await ctx.guild.create_category_channel("rival")
            else:
                new_cat = ctx.guild.get_channel(category.id)
            embed = discord.Embed(title="Rival Interface", description="Click the buttons below to control your voice channel   \u200b", url="https://rival.rocks/discord", color=self.bot.color).add_field(name="Button Usage", inline=True, value=f"{lock} ・ [`Lock`](https://discord.gg/rivalbot) the voice channel\n{unlock} ・ [`Unlock`](https://discord.gg/rivalbot) the voice channel\n{ghost} ・ [`Ghost`](https://discord.gg/rivalbot) the voice channel\n{unghost} ・ [`Reveal`](https://discord.gg/rivalbot) the voice channel\n{claim} ・ [`Claim`](https://discord.gg/rivalbot) the voice channel\n{permit} ・ [`Permit`](https://discord.gg/rivalbot) a member\n{unpermit} ・ [`Reject`](https://discord.gg/rivalbot) a member\n{rename} ・ [`Rename`](https://discord.gg/rivalbot) the channel\n{transfer} ・ [`Transfer`](https://discord.gg/rivalbot) channel ownership\n{delete} ・ [`Delete`](https://discord.gg/rivalbot) the channel")
            #embed.add_field(name="<:lock:1009263067193942117> Lock", value="Lock` your channel so that other members cannot join it.", inline=False)
            #embed.add_field(name="<:unlock2:1009376645125259284> Unlock", value="Unlock's your channel so others may join it.", inline=False)
           # embed.add_field(name="<:ghost:1009227118942634084> Ghost", value="Make your channel invisible", inline=False)
           # embed.add_field(name="<:unghost:1009227230490132580> UnGhost", value="Make your channel visible", inline=False)
           # embed.add_field(name="<a:aw_whiteuser:1009275774668390492> Claim", value = "Claim ownership of the channel after the owner leaves", inline=False)
            #embed.add_field(name="<:trash:1005550877861494814> Delete", value="Delete your channel.", inline=False)
            embed.set_footer(text="The Rival Team", icon_url="https://rival.rocks/invite")
            ch=await ctx.guild.create_text_channel("interface", category=new_cat)
            await ch.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False))
            msg2=await ch.send(embed=embed, view=PersistentView(self.bot))
            channel = await ctx.guild.create_voice_channel("Join To Create", category=new_cat)
            await self.bot.db.execute("""INSERT INTO guild_vm VALUES(%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE guild_id = VALUES(guild_id) AND category = VALUES(category) AND channel = VALUES(channel) AND msg_channel_id = VALUES(msg_channel_id) AND msg_id = VALUES(msg_id)""", ctx.guild.id, new_cat.id, channel.id, ch.id, msg2.id)
            embed2 = discord.Embed(description=f"""{self.em.yes} **Rival's voicemaster has now been setup!** You can use the commands to control it!""", color=self.em.good) 
            await msg.edit(embed=embed2)
        else:
            failembed = discord.Embed(description=f"{self.em.warn} **The voicemaster module is already enabled therefore, there is nothing to setup**", color=self.em.error)
            return await ctx.send(embed=failembed)

    @voice.command(name='unsetup',description="Disable the voicemaster module ",aliases=['disable','off','false'],extras={'perms':"Manage_Channels"}, usage="```Swift\nSyntax: !vm unsetup\nExample: !vm unsetup```")
    @commands.has_permissions(manage_channels=True)
    async def voice_unsetup(self, ctx):
        if await self.bot.db.execute("""SELECT * FROM guild_vm WHERE guild_id = %s""", ctx.guild.id):
            check = await self.bot.db.execute("""SELECT channel,msg_channel_id FROM guild_vm WHERE guild_id = %s""", ctx.guild.id)
            if check:
                try:
                    for channel,msg_channel_id in check:
                        ch=ctx.guild.get_channel(channel)
                        ms=ctx.guild.get_channel(msg_channel_id)
                        await ch.delete()
                        await ms.category.delete()
                        await ms.delete()
                except:
                    pass
            await self.bot.db.execute("""DELETE FROM guild_vm WHERE guild_id = %s""", ctx.guild.id)
            return await util.send_good(ctx, f"rival's voicemaster has been `disabled`")
        else:
            return await util.send_error(ctx, f"rival's voicemaster isn't setup")

    @voice.command(name='permit', aliases=['allow','perm'], description='allow a specific member to join your voice channel', extras={'perms':'Channel Owner'}, brief='member', usage='```Swift\nSyntax: !voicemaster permit <member>\nExample: !voicemaster permit @cop#0001```')
    async def voice_permit(self, ctx, *, member:discord.Member):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    for channel_id in check2:
                        ch=ctx.guild.get_channel(channel_id[0])
                        await ch.set_permissions(member, connect=True)
                    return await util.send_good(ctx, f"you have `allowed` {member.mention} to join")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name='transfer', aliases=['promote'], description='transfer ownership of the vc to another member', extras={'perms':'Channel Owner'}, brief='member', usage='```Swift\nSyntax: !voicemaster transfer <member>\nExample: !voicemaster transfer @cop#0001```')
    async def voice_transfer(self, ctx, *, member:discord.Member):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    if member.voice:
                        await self.bot.db.execute("""DELETE FROM vm_data WHERE channel_id = %s""", ctx.author.voice.channel.id)
                        await self.bot.db.execute("""INSERT INTO vm_data VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE guild_id = VALUES(guild_id) AND user_id = VALUES(user_id) AND owner_id = VALUES(owner_id)""", member.voice.channel.id, ctx.guild.id, member.id, member.id)
                        return await util.send_good(ctx, f"you have given `ownership` to  {member.mention}")
                    else:
                        return await util.send_error(ctx, f"no voice channel found with {member.mention} in it")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name='unpermit', aliases=['deny','unperm'],description='unallow a specific member to join your voice channel', extras={'perms':'Channel Owner'}, brief='member', usage='```Swift\nSyntax: !voicemaster unpermit <member>\nExample: !voicemaster unpermit @cop#0001```')
    async def voice_unpermit(self, ctx, *, member:discord.Member):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    if member in ctx.author.voice.channel.members:
                        await member.edit(voice_channel=None)
                    await ctx.author.voice.channel.set_permissions(member, connect=False)
                    return await util.send_good(ctx, f"you have `unallowed` {member.mention} to join")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name='delete', aliases=['del'], description="delete your voice channel", extras={'perms':'Channel Owner'})
    async def voice_delete(self, ctx):
        try:
            if ctx.author.voice.channel:
                check=await self.bot.db.execute("""SELECT channel_id FROM vm_data WHERE owner_id = %s AND guild_id = %s""", ctx.author.id, ctx.guild.id, one_value=True)
                if check:
                    ch=ctx.guild.get_channel(int(check))
                    await ch.delete()
                    return await util.send_good(ctx, f"deleted your voice channel")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name='lock',description="Lock's your channel so that other members cannot join it.",extras={'perms':'Channel Owner'})
    async def voice_lock(self, ctx):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=False)
                    return await util.send_good(ctx, f"your `voicemaster` channel has been `locked`")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name='ghost',description="Ghosts your channel so that other members cannot see it",extras={'perms':'Channel Owner'})
    async def voice_ghost(self, ctx):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=False)
                    return await util.send_good(ctx, f"your `voicemaster` channel has been `ghosted`")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name='unghost',description="Unghosts your channel so that other members can see it",extras={'perms':'Channel Owner'})
    async def voice_unghost(self, ctx):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, view_channel=None)
                    return await util.send_good(ctx, f"your `voicemaster` channel has been `unghosted`")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name='unlock',description="Unlock's your channel so others may join it",extras={'perms':'Channel Owner'})
    async def voice_unlock(self, ctx):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    await ctx.author.voice.channel.set_permissions(ctx.guild.default_role, connect=True)
                    return await util.send_good(ctx, f"your `voicemaster` channel has been `unlocked`")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")
    

    @voice.command(name='limit',description="Set a limit to your channel so only a certain amount may join",brief="limit",usage="```Swift\nSyntax: !voicemaster limit [limit]\nExample: !voicemaster limit```",extras={'perms':'Channel Owner'})
    async def voice_limit(self, ctx, limit: int):
        try:
            if ctx.author.voice.channel:
                check2=await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    channel = ctx.author.voice.channel
                    if limit <99:
                        await channel.edit(user_limit=limit)
                        return await util.send_good(ctx, f"your voicemaster channel limit has been set to `{limit}`")
                    else:
                        return await util.send_error(ctx, f"Limit must be smaller than `99`")
                else:
                    return await util.send_error(ctx, f"you are not the channel owner")
            else:
                return await util.send_error(ctx, f"you're not connected to your voicemaster channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")

    @voice.command(name="claim",description="Claim the voice channel if the creator leaves",usage="```Swift\nExample: voicemaster claim```")
    async def voice_claim(self, ctx):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT owner_id FROM vm_data WHERE channel_id = %s""", ctx.author.voice.channel.id, one_value=True)
                c2=ctx.guild.get_member(check2)
                if c2 in ctx.author.voice.channel.members:
                    return await util.send_error(ctx, f"the owner is still in the voice channel")
                else:
                    c=ctx.author.voice.channel
                    try:
                        owner=ctx.guild.get_member(await self.bot.db.execute("""SELECT owner_id FROM vm_data WHERE channel_id = %s""", c.id, one_value=True))
                    except:
                        owner=await self.bot.fetch_user(check2)
                    if ctx.author.voice.channel.name == f"{owner.name}'s channel":
                        await c.edit(name=f"{ctx.author.name}'s channel")
                    await self.bot.db.execute("""INSERT INTO vm_data VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE owner_id = VALUES(owner_id)""", ctx.author.voice.channel.id, ctx.guild.id, ctx.author.id, ctx.author.id)
                    return await util.send_good(ctx, f"you are now the channel owner")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")
    
    
    @voice.command(name='name',description="Change the name of your channel",brief="name",usage="```Swift\nSyntax: !voicemaster name [name]\nExample: !voicemaster name```", extras={'perms':'Channel Owner'})
    async def voice_name(self, ctx, *, name: str):
        try:
            if ctx.author.voice.channel:
                check2 = await self.bot.db.execute("""SELECT * FROM vm_data WHERE channel_id = %s AND owner_id = %s""", ctx.author.voice.channel.id, ctx.author.id)
                if check2:
                    await ctx.author.voice.channel.edit(name=name)
                    return await util.send_good(ctx, f"your `voicemaster` channel has been renamed to `{name}`")
                else:
                    return await util.send_error(ctx, "you don't own this channel")
            else:
                return await util.send_error(ctx, f"you aren't connected to a voice channel")
        except:
            return await util.send_error(ctx, f"you aren't connected to a voice channel")


async def setup(bot):
    await bot.add_cog(VoiceMasterr(bot))