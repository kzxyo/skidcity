const { MessageEmbed } = require('discord.js')
const { prefix, embedcolor, support, cmdcount } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "help",
  aliases: ['h'],
  description: `shows all available bot commands`,
  usage: '{guildprefix}help\n{guildprefix}help [command]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const command = client.commands.get(args[0]) || client.commands.get(client.aliases.get(args[0]))
  
    if (command) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}${command.name}`)
      .setDescription(`${command.description}`)

      if (command.subcommands) {

        let subcommands = command.subcommands

        subcommands = subcommands.replaceAll('{guildprefix}', guildprefix)

        embed.addField('**subcommands**', `${subcommands}`, false)
      }

      let usage = command.usage

      usage = usage.replaceAll('{guildprefix}', guildprefix)

      //if (command.subcommands) embed.addField('**subcommands**', `${subcommands}`, false)
      if (command.usage) embed.addField('**usage**', `${usage}`, false)
      if (command.aliases) embed.addField('**aliases**', `${command.aliases.join(', ')}`, false)

      return message.channel.send({ embeds: [embed] })

    } else if (args.length > 0) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`this isn't a command, use \`help\` for a list of commands`)
      .setFooter({ text: `join the support: ${support} • ${cmdcount} commands` })

      return message.channel.send({ embeds: [embed] })

    } else {

      return message.channel.send(`${message.author} <https://scare.life/commands>, or join support server at <https://scare.life/discord>`)
    }
  }
}