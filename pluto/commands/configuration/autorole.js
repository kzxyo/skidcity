const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const autoroleschema = require('../../database/autorole')

module.exports = {
  name: "autorole",
  aliases: ['joinrole', 'autoroles'],
  description: `automatically assign role(s) to a member on join`,
  subcommands: '{guildprefix}autorole add - adds a role to assign on join\n{guildprefix}autorole clear - clear all autoroles\n{guildprefix}autorole list - list all the autoroles\n{guildprefix}autorole remove - removes an autorole',
  usage: '{guildprefix}autorole',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) return message.channel.send(`this command requires \`administrator\` permission`)

    if (args[0] === 'add') {

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1])

      if (!role) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}autorole add`)
        .setDescription('adds a role to assign on join')
        .addFields(
        { name: '**usage**', value: `${guildprefix}autorole add [role]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      const autoroledata = await autoroleschema.findOne({ GuildID: message.guild.id })

      if (autoroledata) {
        await autoroleschema.findOneAndRemove({
          GuildID: message.guild.id,
        });

        let newdata = new autoroleschema({
          GuildID: message.guild.id,
          RoleID: role.id,
        });
        
        newdata.save();

        return message.channel.send(`**${role.name}** has been set as the auto role 👍`)
      } else if (!autoroledata) {

        let newdata = new autoroleschema({
          GuildID: message.guild.id,
          RoleID: role.id,
        });
        
        newdata.save();

        return message.channel.send(`**${role.name}** has been set as the auto role 👍`)
    }

    } else if (args[0] === 'clear') {

      const autoroledata = await autoroleschema.findOne({ GuildID: message.guild.id })

      if (autoroledata) {

        await autoroleschema.findOneAndRemove({ GuildID: message.guild.id });

        return message.channel.send(`the auto role has been cleared`)

      } else {
        
        return message.channel.send('no auto roles found')
      }

    } else if (args[0] === 'list') {

      const autoroledata = await autoroleschema.findOne({ GuildID: message.guild.id })

      if (autoroledata) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle('auto roles')
        .setDescription(`<@${autoroledata.RoleID}>`)

        return message.channel.send({ embeds: [embed] })

      } else {
        return message.channel.send('no auto roles found')
      }

    } else if (args[0] === 'remove' || args[0] === 'rm' || args[0] === 'delete' || args[0] === 'del') {
   
      const autoroledata = await autoroleschema.findOne({ GuildID: message.guild.id })

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1])

      if (!role) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}autorole remove`)
        .setDescription('removes an autorole')
        .addFields(
        { name: '**usage**', value: `${guildprefix}autorole remove [role]`, inline: false },
        { name: '**aliases**', value: `rm, delete, del`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (autoroledata) {
        await autoroleschema.findOneAndRemove({
          GuildID: message.guild.id,
        });

        return message.channel.send(`auto roles have been cleared 👍`) 
      } else if (!autoroledata) {
        return message.channel.send(`there is no auto role`) 
      }

    } else {
        
      const embed = new MessageEmbed()
    
      .setColor(embedcolor)
      .setTitle(`${guildprefix}autorole`)
      .setDescription(`automatically assign role(s) to a member on join`)
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}autorole add - adds a role to assign on join\n${guildprefix}autorole clear - clear all autoroles\n${guildprefix}autorole list - list all the autoroles\n${guildprefix}autorole remove - removes an autorole`, inline: false },
      { name: '**usage**', value: `${guildprefix}autorole`, inline: false },
      { name: '**aliases**', value: 'joinrole, autoroles', inline: false },
      )
    
      return message.channel.send({ embeds: [embed] })
    }
  }
}