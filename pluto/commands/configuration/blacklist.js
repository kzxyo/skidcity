const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "blacklist",
  aliases: ['ignore', 'blist', 'bl'],
  description: `makes pluto ignore a user`,
  subcommands: '{guildprefix}blacklist user - makes pluto ignore a user\n{guildprefix}blacklist list - list all blacklisted users',
  usage: '{guildprefix}blacklist',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) return message.channel.send(`this command requires \`administrator\` permission`)

    if (args[0] === 'user') {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[1])

      if (!user) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}blacklist user`)
        .setDescription('makes pluto ignore a user')
        .addFields(
        { name: '**usage**', value: `${guildprefix}blacklist user [member]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (user.id === client.user.id) return message.channel.send(`you can't blacklist me :clown:`)

      globaldataschema.findOne({ GuildID: message.guild.id }, async function(err, data) {

        if (!data?.BlacklistedUsers.includes(user.id)) {

          data.BlacklistedUsers.push(user.id)
          data.save();

          return message.channel.send(`**${user.user.tag}** will now be ignored 👍`)

        } else {

          let i = data.BlacklistedUsers.indexOf(`${user.id}`)
          data.BlacklistedUsers.splice(i, 1)
          data.save();

          return message.channel.send(`**${user.user.tag}** will no longer be ignored 👍`)
        }
      })
      
    } else if (args[0] === 'list') {

      const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

      const blacklistedusersarray = globaldata.BlacklistedUsers

      let users = "";
      blacklistedusersarray.forEach(guild => {
        users += `<@${guild}>, `;
      });

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .addFields(
      { name: '**blacklisted users**', value: users.length ? `${users}` : "\`none\`", inline: false },
      )
      //.setFooter({ text: `a user will be banned when a limit is hit` })

      return message.channel.send({ embeds: [embed] })

    } else {

      const embed = new MessageEmbed()
    
      .setColor(embedcolor)
      .setTitle(`${guildprefix}blacklist`)
      .setDescription(`makes pluto ignore a user`)
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}blacklist user - makes pluto ignore a user\n${guildprefix}blacklist list - list all blacklisted users`, inline: false },
      { name: '**usage**', value: `${guildprefix}blacklist`, inline: false },
      { name: '**aliases**', value: 'ignore, blist, bl', inline: false },
      )
    
      return message.channel.send({ embeds: [embed] })     
    }
  }
}