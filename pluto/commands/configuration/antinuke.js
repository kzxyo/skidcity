const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "antinuke",
  aliases: ['antiwizz', 'an', 'aw'],
  description: `configurable anti nuke/wizz to limit bans, kicks, channel deletions, and role changes/updates with customizable limits`,
  subcommands: '{guildprefix}antinuke settings - views all antinuke settings/limits\n{guildprefix}antinuke toggle - enable/disable the entire antinuke module\n{guildprefix}antinuke channel - sets antinuke log channel\n{guildprefix}antinuke unwhitelist - unwhitelist a member from antinuke limits\n{guildprefix}antinuke whitelist - whitelist a member from antinuke limits\n{guildprefix}antinuke unwhitelistrole - unwhitelist a role from antinuke limits\n{guildprefix}antinuke whitelistrole - whitelist a role from antinuke limits',
  usage: '{guildprefix}antinuke',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if (message.author.id !== message.guild.ownerId) return message.channel.send(`this command is only available to the guild owner`)

    if (args[0] === 'settings') {

      let antinuketoggle;

      const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

      if (globaldata.AntiNukeToggle === 'true') {
        antinuketoggle = '**enabled**'
      } else {
        antinuketoggle = '**disabled**'
      }

      let antinukechannel;

      if (globaldata.AntiNukeChannel) {
        antinukechannel = `<#${globaldata.AntiNukeChannel}>`
      } else { 
        antinukechannel = '\`none\`'
      }

      const whitelistedusersarray = globaldata.AntiNukeWhitelistedUsers

      let users = "";
      whitelistedusersarray.forEach(guild => {
        users += `<@${guild}>, `;
      });

      const whitelistedrolesarray = globaldata.AntiNukeWhitelistedRoles

      let roles = "";
      whitelistedrolesarray.forEach(guild => {
        roles += `<@&${guild}>, `;
      });

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`status: ${antinuketoggle}`)
      .addFields(
      { name: '**log channel**', value: `${antinukechannel}`, inline: false },
      { name: '**whitelisted users**', value: users.length ? `${users}` : "\`none\`", inline: false },
      { name: '**whitelisted roles**', value: roles.length ? `${roles}` : "\`none\`", inline: false },
      )
      .setFooter({ text: `a user will be banned when a limit is hit` })

      return message.channel.send({ embeds: [embed] })

    } else if (args[0] === 'toggle') {

      const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

      if (globaldata.AntiNukeToggle) {

        globaldata.AntiNukeToggle = 'false';

        await globaldata.save();

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`anti nuke has been turned **off**`)

        return message.channel.send({ embeds: [embed] })

      } else {

        globaldata.AntiNukeToggle = 'true';

        await globaldata.save();

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`anti nuke has been turned **on**`)

        return message.channel.send({ embeds: [embed] })
      }

    } else if (args[0] === 'channel' || args[0] === 'c') {

      if (args[1] === 'none') {

        if (globaldata.AntiNukeChannel) {

          globaldata.AntiNukeChannel = null;

          await globaldata.save();

          return message.channel.send('removed log channel 👍')     
        } else {
          return message.channel.send('there is no log channel') 
        }
        
      } else {

        const logchannel = message.mentions.channels.first() || client.guilds.cache.get(message.guild.id).channels.cache.get(args[1])

        if (!logchannel || logchannel.type !== 'GUILD_TEXT' && logchannel.type !== 'GUILD_NEWS') {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setTitle(`${guildprefix}antinuke channel`)
          .setDescription('set where to send welcome messages')
          .addFields(
          { name: '**usage**', value: `${guildprefix}antinuke channel [channel]\n${guildprefix}antinuke channel none`, inline: false },
          { name: '**aliases**', value: `c`, inline: false },
          )

          return message.channel.send({ embeds: [embed] })
        }

        if (globaldata.AntiNukeChannel) {

          globaldata.AntiNukeChannel = logchannel.id;

          await globaldata.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${logchannel} is now set as logs`)

          return message.channel.send({ embeds: [embed] })

        } else {

          globaldata.AntiNukeChannel = logchannel.id;

          await globaldata.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${logchannel} is now set as logs`)

          return message.channel.send({ embeds: [embed] })
        }    
      }

    } else if (args[0] === 'unwhitelist' || args[0] === 'uwl') {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[1])

      if (!user) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}antinuke unwhitelist`)
        .setDescription('unwhitelist a member from antinuke limits')
        .addFields(
        { name: '**usage**', value: `${guildprefix}antinuke unwhitelist [member]`, inline: false },
        { name: '**aliases**', value: `uwl`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      globaldataschema.findOne({ GuildID: message.guild.id }, async function(err, data) {

        if (!data?.AntiNukeWhitelistedUsers.includes(user.id)) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${user} isn't whitelisted`)
      
          return message.channel.send({ embeds: [embed] })  

        } else {

          let i = data.AntiNukeWhitelistedUsers.indexOf(`${user.id}`)
          data.AntiNukeWhitelistedUsers.splice(i, 1)
          data.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${user} is no longer whitelisted`)

          return message.channel.send({ embeds: [embed] })
        }
      })

    } else if (args[0] === 'whitelist' || args[0] === 'wl') {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[1])

      if (!user) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}antinuke whitelist`)
        .setDescription('whitelist a member from antinuke limits')
        .addFields(
        { name: '**usage**', value: `${guildprefix}antinuke whitelist [member]`, inline: false },
        { name: '**aliases**', value: `wl`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      globaldataschema.findOne({ GuildID: message.guild.id }, async function(err, data) {

        if (data?.AntiNukeWhitelistedUsers.includes(user.id)) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${user} is already whitelisted!`)
      
          return message.channel.send({ embeds: [embed] })  

        } else {

          data.AntiNukeWhitelistedUsers.push(user.id)
          data.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${user} has been whitelisted`)

          return message.channel.send({ embeds: [embed] })
        }
      })

    } else if (args[0] === 'unwhitelistrole' || args[0] === 'uwlr') {

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1])

      if (!role) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}antinuke unwhitelistrole`)
        .setDescription('unwhitelist a role from antinuke limits')
        .addFields(
        { name: '**usage**', value: `${guildprefix}antinuke unwhitelistrole [role]`, inline: false },
        { name: '**aliases**', value: `uwlr`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      globaldataschema.findOne({ GuildID: message.guild.id }, async function(err, data) {

        if (!data?.AntiNukeWhitelistedRoles.includes(role.id)) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${role} isn't whitelisted`)
      
          return message.channel.send({ embeds: [embed] })  

        } else {

          let i = data.AntiNukeWhitelistedRoles.indexOf(`${role.id}`)
          data.AntiNukeWhitelistedRoles.splice(i, 1)
          data.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${role} is no longer whitelisted`)

          return message.channel.send({ embeds: [embed] })
        }
      })

    } else if (args[0] === 'whitelistrole' || args[0] === 'wlr') {

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1])

      if (!role) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}antinuke whitelistrole`)
        .setDescription('whitelist a role from antinuke limits')
        .addFields(
        { name: '**usage**', value: `${guildprefix}antinuke whitelistrole [role]`, inline: false },
        { name: '**aliases**', value: `wlr`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      globaldataschema.findOne({ GuildID: message.guild.id }, async function(err, data) {

        if (data?.AntiNukeWhitelistedRoles.includes(role.id)) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${role} is already whitelisted!`)
      
          return message.channel.send({ embeds: [embed] })  

        } else {

          data.AntiNukeWhitelistedRoles.push(role.id)
          data.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${role} has been whitelisted`)

          return message.channel.send({ embeds: [embed] })
        }
      })

    } else {
        
      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}antinuke`)
      .setDescription('configurable anti nuke/wizz to limit bans, kicks, channel deletions, and role changes/updates with customizable limits')
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}antinuke settings - views all antinuke settings/limits\n${guildprefix}antinuke toggle - enable/disable the entire antinuke module\n${guildprefix}antinuke channel - sets antinuke log channel\n${guildprefix}antinuke unwhitelist - unwhitelist a member from antinuke limits\n${guildprefix}antinuke whitelist - whitelist a member from antinuke limits\n${guildprefix}antinuke unwhitelistrole - unwhitelist a role from antinuke limits\n${guildprefix}antinuke whitelistrole - whitelist a role from antinuke limits`, inline: false },
      { name: '**usage**', value: `${guildprefix}antinuke`, inline: false },
      { name: '**aliases**', value: 'antiwizz, an, aw', inline: false },
      )
    
      return message.channel.send({ embeds: [embed] })
    }
  }
}