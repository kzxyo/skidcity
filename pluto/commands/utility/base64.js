const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const base64 = require("js-base64")

module.exports = {
  name: "base64",
  aliases: ['b64', 'decode'],
  description: "decode a base64 string",
  usage: '{guildprefix}base64 [string]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires \`manage messages\` permission`)

    if (!args[0]) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}base64`)
      .setDescription('decode a base64 string')
      .addFields(
      { name: '**usage**', value: `${guildprefix}base64 [string]`, inline: false },
      { name: '**aliases**', value: 'b64, decode', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    let name = args.join(' ')

    let decode = base64.decode(name);

    message.channel.send({ content: `\`\`\`${decode}\`\`\`` })
  }
}