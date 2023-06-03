const client = require('../bleed')
const db = require('quick.db')
const { default_prefix, color } = require("../config.json");
const Discord = require('discord.js')

client.on("guildMemberAdd", async member => {

  var antiNew = db.get(`anti-new_${member.guild.id}`);
  if (antiNew == null) { antiNew = false; }

  if (antiNew) { if (member.user.createdTimestamp + 1210000000 > Date.now()) { member.kick() } }

  const newMember = member
  const role = member.guild.roles.cache.find(r => r.id === db.get(`autorole_${member.guild.id}`));
  if (role) member.roles.add(role);
  const logs = db.get(`logschannel_${member.guild.id}`);
  if (logs === null) {
    return;
  }

  if (role === null) return;

  const embed = new Discord.MessageEmbed()
    .setAuthor(newMember.user.tag, newMember.user.avatarURL())
    .setTitle(`**Autorole**`)
    .addField(`**Member**`, `<@` + newMember + `>`)
    .addField(`**Role**`, `${role}`)
    .setColor(`${color}`)
    .setTimestamp()
  if (newMember) await newMember.roles.add(role);
  if (logs) await client.channels.cache.get(logs).send(embed);

  const embed2 = new Discord.MessageEmbed()
    .setAuthor(newMember.user.tag, newMember.user.avatarURL())
    .setDescription(`<@` + newMember + `>` + ` has joined ${newMember.guild.name}`)
    .setColor(`${color}`)
    .setTimestamp()
  await client.channels.cache.get(logs).send(embed2)
})

client.on("guildMemberAdd", async member => {
  let chx = db.get(`welchannel_${member.guild.id}`);
  if (chx === null) {
    return;
  }
  let welcome = db.get(`welmessage_${member.guild.id}`);
  if (welcome === null) {
    return;
  }

  welcome = welcome.replace('{user}', member);
  welcome = welcome.replace('{user.name}', member.username);
  welcome = welcome.replace('{user.tag}', member.tag);
  welcome = welcome.replace('{user.id}', member.id);
  welcome = welcome.replace('{membercount}', member.guild.memberCount);
  const ordinal = (member.guild.memberCount.toString().endsWith(1) && !member.guild.memberCount.toString().endsWith(11)) ? 'st' : (member.guild.memberCount.toString().endsWith(2) && !member.guild.memberCount.toString().endsWith(12)) ? 'nd' : (member.guild.memberCount.toString().endsWith(3) && !member.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
  welcome = welcome.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
  welcome = welcome.replace('{guild.name}', member.guild.name);
  welcome = welcome.replace('{guild.id}', member.guild.id);

  if (welcome) await client.channels.cache.get(chx).send(welcome)
});

client.on('guildMemberAdd', member =>{
  if(member.user.bot) {
    member.ban()
  }
});
const joinSchema = require('../models/joindmmodel')
client.on('guildMemberAdd', async (member) => {
  joinSchema.findOne({ guildId: member.guild.id }, async(err, data) => {
    if(!data) return;

    const user = member.user
    const joindm = data.Message
    const toSend = joindm.replace('{user.mention}', member.user).replace('{user}', member.user.username).replace('{user.tag}', member.user.tag).replace('{guild.id}', member.guild.id).replace('{guild.name}', member.guild.name)

    user.send(toSend)
})
})