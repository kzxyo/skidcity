const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')
const { deny } = require('../../emojis.json')

module.exports = {
  name: "unban",
  category: "moderation",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`ban_members\`` } });
    if (!message.guild.me.hasPermission("BAN_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`ban_members\`` } });


    let reason = args.slice(1).join(" ");
    let userID = args[0];

    if (!reason) reason = 'No reason given.';
    const ubhelpEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: unban')
      .setDescription('Unbans the mentioned user from the guild')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'member, reason', true)
      .addField('**Information**', `${warn} Ban Members`, true)
      .addField('**Usage**', '\`\`\`Syntax: unban (member) <reason>\nExample: unban four#0001 Forgiven\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(ubhelpEmbed)
    if (isNaN(args[0])) return message.channel.send(ubhelpEmbed)
    message.guild.fetchBans().then(async bans => {
      if (bans.size == 0) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Couldn't find any bans for this guild`}});
      let bUser = bans.find(b => b.user.id == userID);
      if (!bUser) return message.channel.send({ embed: { color: "#fe6464", description: `${deny} ${message.author}: Couldn't find a ban for: **${userID}**` } })
      await message.guild.members.unban(bUser.user, reason).catch(err => {
        console.log(err);
        return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Something went wrong **unbanning** that ID` } });
      }).then(() => {
        message.channel.send('👍')
      })
    })
  }
}