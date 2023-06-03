const { Message } = require('discord.js')
const Discord = require('discord.js');
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: 'mute',

  /**
   * @param {Message} message
   */

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\``}});
    if (!message.guild.me.hasPermission("MUTE_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`mute_members\``}});

    const muteEmbed = new Discord.MessageEmbed()
    .setAuthor(message.author.username, message.author.avatarURL({
      dynamic: true
    }))
    .setTitle('Command: mute')
    .setDescription('Mutes the mentioned member in all channels')
    .addField('**Aliases**', 'N/A', true)
    .addField('**Parameters**', 'member', true)
    .addField('**Information**', `${warn} Manage Messages`, true)
    .addField('**Usage**', '\`\`\`Syntax: mute <member>\nExample: mute four#0001\`\`\`')
    .setFooter(`Module: moderation`)
    .setTimestamp()
    .setColor(color)
    if (!args[0]) return message.channel.send(muteEmbed)

    let user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

    const Member = message.mentions.members.first() || message.guild.members.cache.get(args[0])
    if (Member.id == message.author.id) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot mute **yourself**` } })
    if (message.member.roles.highest.comparePositionTo(Member.roles.highest) >= 0) return message.channel.send({ embed: { color: "fe6464", description: `${deny} ${message.author}: You cannot mute someone that is **higher** than **yours**` } })
    if (!Member) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: I was unable to find a member with that name` } })
    const role = message.guild.roles.cache.find(role => role.name.toLowerCase() === 'muted')
    if (!role) {
      try {
        message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: There was no **muted** role found` } }).then(embedMessage => {
          embedMessage.edit({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Attempting to create a **muted** role` } })
        });

        let muterole = await message.guild.roles.create({
          data: {
            name: 'muted',
            permissions: []
          }
        });
        message.guild.channels.cache.filter(c => c.type === 'text').forEach(async (channel, id) => {
          await channel.createOverwrite(muterole, {
            SEND_MESSAGES: false,
            ADD_REACTIONS: false
          })
        });
        message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Sucessfully created a **muted** role` } })
      } catch (error) {
        console.log(error)
        message.channel.send(error)
      }
    };
    let role2 = message.guild.roles.cache.find(r => r.name.toLowerCase() === 'muted')
    if (Member.roles.cache.has(role2.id)) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: **${user.user.tag}** has already been muted` } })
    await Member.roles.add(role2)
    message.channel.send({ embed: { color: "RED", description: `${message.author}: **${user.user.tag}** is now muted` } })
  }
}