const db = require('quick.db')
const discord = require('discord.js')
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "welcome",
  aliases: ['welc', 'wlc'],

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });

    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };
    if (message.author.bot) return;
    const embed = new discord.MessageEmbed()
      .setTitle(`**${prefix}welcome**`)
      .setDescription(`set up a welcome message when new members join`)
      .addField(`**subcommands**`, `${prefix}welcome channel ＊ set where to send welcome messages\n${prefix}welcome clear ＊ clear the welcome message\n${prefix}welcome message ＊ set the welcome message text\n${prefix}welcome variables ＊ see all the welcome message variables`)
      .addField(`**usage**`, `${prefix}welcome`)
      .addField(`**aliases**`, `welc, wlc`)
      .setColor(color)
    if (!args[0]) return message.channel.send(embed)
    if (args[0].toLowerCase() == 'message') {
      db.set(`welmessage_${message.guild.id}`, args.splice(1).join(' '))
      let wlcmsg = db.get(`welmessage_${message.guild.id}`)
      if (wlcmsg === null) {
        const setmsgembed = new discord.MessageEmbed()
          .setDescription(`${warn} ${message.author}: There is no **welcome message** set one with \`${prefix}welcome message\``)
          .setColor(`#efa23a`)
        return message.channel.send(setmsgembed)
      } else {
        const setembed = new discord.MessageEmbed()
          .setTitle("welcome message:")
          .setDescription(`\`\`\`` + wlcmsg + `\`\`\``)
          .setFooter(`see the varibles with ${prefix}welcome variables + test with ${prefix}welcome test\ndisable with ${prefix}welcome clear`)
          .setColor(color)
        return message.channel.send(setembed)
      }
    } else if (args[0].toLowerCase() == 'test') {
      let chx = db.get(`welchannel_${message.guild.id}`);
      if (chx === null) {
        return;
      }
      let welcome = db.get(`welmessage_${message.guild.id}`);
      if (welcome === null) {
        return;
      }
      welcome = welcome.replace('{user}', message.member);
      welcome = welcome.replace('{user.name}', message.author.username);
      welcome = welcome.replace('{user.tag}', message.author.tag);
      welcome = welcome.replace('{user.id}', message.author.id);
      welcome = welcome.replace('{membercount}', message.member.guild.memberCount);
      const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
      welcome = welcome.replace('{membercount.ordinal}', message.member.guild.memberCount + ordinal);
      welcome = welcome.replace('{guild.name}', message.member.guild.name);
      welcome = welcome.replace('{guild.id}', message.member.guild.id);

      client.channels.cache.get(chx).send(welcome)
      message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Successfully tested your **welcome message** in <#` + chx + `>` } })
      if (chx === null) {
        return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: There is no **welcome channel** set for me to test this` } })
      }
    } else if (args[0].toLowerCase() == 'variables') {
      const member = message.author
      const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
      const variablesembed = new discord.MessageEmbed()
        .setTitle(`welcome variables`)
        .setDescription(`\`{user}\` ＊ <@` + member + `>\n\`{user.name}\` ＊ ` + message.author.username + `\n\`{user.tag}\` ＊ ` + message.author.tag + `\n\`{user.id}\` ＊ ` + message.author.id + `\n\`{guild.name}\` ＊ ` + message.member.guild.name + `\n\`{guild.id}\` ＊ ` + message.member.guild.id + `\n\`{membercount}\` ＊ ` + message.member.guild.memberCount + `\n\`{membercount.ordinal}\` ＊ ` + message.member.guild.memberCount + ordinal)
        .setColor(color)
      message.channel.send(variablesembed)
    } else if (args[0].toLowerCase() == "channel") {
      let channel = message.mentions.channels.first()
      if (!channel) {
        const welcomechannel = new discord.MessageEmbed()
          .setTitle(`${prefix}welcome channel`)
          .setDescription(`set the channel 4 welcome msgs`)
          .addField(`**usage**`, `${prefix}welcome channel [#channel]`)
          .addField(`**aliases**`, `c, chan`)
          .setColor(color)
        return message.channel.send(welcomechannel)
      }
      db.set(`welchannel_${message.guild.id}`, channel.id)
      await message.channel.send(`Set the welcome channel to ${channel}`)
    } else if (args[0].toLowerCase() == "chan") {
      let channel = message.mentions.channels.first()
      if (!channel) {
        const welcomechannel = new discord.MessageEmbed()
          .setTitle(`${prefix}welcome channel`)
          .setDescription(`set the channel 4 welcome msgs`)
          .addField(`**usage**`, `${prefix}welcome channel [#channel]`)
          .addField(`**aliases**`, `c, chan`)
          .setColor(color)
        return message.channel.send(welcomechannel)
      }
      db.set(`welchannel_${message.guild.id}`, channel.id)
      await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Set the **welcome channel** to ${channel}` } })
    } else if (args[0].toLowerCase() == "c") {
      let channel = message.mentions.channels.first()
      if (!channel) {
        const welcomechannel = new discord.MessageEmbed()
          .setTitle(`${prefix}welcome channel`)
          .setDescription(`set the channel 4 welcome msgs`)
          .addField(`**usage**`, `${prefix}welcome channel [#channel]`)
          .addField(`**aliases**`, `c, chan`)
          .setColor(color)
        return message.channel.send(welcomechannel)
      }
      db.set(`welchannel_${message.guild.id}`, channel.id)
      await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Set the **welcome channel** to ${channel}` } })
    } else if (args[0].toLowerCase() == "clear") {
      db.delete(`welchannel_${message.guild.id}`)
      db.delete(`welmessage_${message.guild.id}`)
      return await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Successfully cleared the **welcome channel** & **message**` } })
    }
  }
}