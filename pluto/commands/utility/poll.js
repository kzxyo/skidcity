const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "poll",
  aliases: ['vote'],
  description: 'sets up a poll using reactions',
  usage: '{guildprefix}poll [question]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires \`manage messages\` permission`)

    const pollquestion = args.join(" ");

    if (!pollquestion) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}poll`)
      .setDescription('sets up a poll')
      .addFields(
      { name: '**usage**', value: `${guildprefix}poll [question]`, inline: false },
      { name: '**aliases**', value: 'vote', inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle(pollquestion)
    .setDescription(`1️⃣ yes\n2️⃣ no`)
    .setFooter({ text: `started by ${message.author.tag}`, iconURL: `${message.author.displayAvatarURL({ dynamic: true })}` })

    let messageEmbed = await message.channel.send({ embeds: [embed] })
    messageEmbed.react('1️⃣').catch(() => { return; })
    messageEmbed.react('2️⃣').catch(() => { return; })
  }
}