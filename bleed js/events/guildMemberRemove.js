const client = require('../bleed')
const db = require('quick.db')
const { default_prefix, color } = require("../config.json");
const Discord = require("discord.js")

client.on("guildMemberRemove", async member => {

  const MemberLeft = member
  let logs = db.get(`logschannel_${member.guild.id}`);
  if (!logs) {
    return;
  }
  const embed = new Discord.MessageEmbed()
    .setAuthor(MemberLeft.user.tag, MemberLeft.user.avatarURL())
    .setDescription(`<@` + MemberLeft + `>` + ` has left ${MemberLeft.guild.name}`)
    .setColor(`${color}`)
    .setTimestamp()
  const cachedLogs = await client.channels.fetch(logs)
  cachedLogs.send(embed);
})