const { MessageEmbed } = require('discord.js')
const { embedcolor } = require('./../../config.json')
const moment = require('moment')

module.exports = {
  name: "userinfo",
  aliases: ['lookup', 'whois', 'uinfo', 'user', 'profile', 'ui'],
  description: "get information on any discord user",
  usage: '{guildprefix}userinfo\n{guildprefix}userinfo [user]',
  run: async(client, message, args) => {

    const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

    let userroles = user.roles.cache
    .map((x) => x)
    .filter((z) => z.name !== "@everyone");

    if (userroles.length > 100) {
      userroles = "100+";
    }

    if (userroles.length < 1) {
      userroles = "none";
    }

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle(`${user.user.tag}`)
    .addFields( 
    { name: '**dates**', value: `**registered**: ${moment(user.user.createdAt).format("MM/DD/YYYY, h:mm A")}\n**joined**: ${moment(user.joinedAt).format("MM/DD/YYYY, h:mm A")}`, inline: false },
    { name: '**roles**', value: `${userroles}`, inline: false },
    { name: '**userid**', value: `\`${user.id}\``, inline: false },
    )
    .setThumbnail(user.user.displayAvatarURL({size: 512, dynamic: true}))

    message.channel.send({ embeds: [embed] })
  }
}