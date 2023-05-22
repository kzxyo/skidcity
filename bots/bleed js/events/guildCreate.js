const client = require('../bleed')
const { default_prefix, color } = require("../config.json");
const Discord = require('discord.js')
const { warn } = require('../emojis.json')

client.on("guildCreate", guild => {
  const embed = new Discord.MessageEmbed()
    .setDescription(`Joined new guild: **${guild.name}**, owned by ${guild.owner.user.tag} (\`${guild.id}\`) | ${guild.memberCount} members`)
    .setColor(`#a3eb7b`)
  client.channels.cache.get("868302839947100160").send(embed)
})

client.on("guildCreate", guild => {
  let channelToSend;

  guild.channels.cache.forEach((channel) => {
    if (
      channel.type === "text" &&
      !channelToSend &&
      channel.permissionsFor(guild.me).has("SEND_MESSAGES")
    ) channelToSend = channel;
  });

  const embed = new Discord.MessageEmbed()
    .setColor(color)
    .setThumbnail(client.user.displayAvatarURL({ size: 2048 }))
    .setTitle(`Getting started with ${client.user.username}`)
    .setDescription(`Hey! Thanks for your interest in **${client.user.username} bot**. The following will provide you with some tips on how to get started with your server!`)
    .addField(`**Prefix :robot:**`, `The most important thing is my prefix. It is set to \`,\` by default for this server and it is also customizable, so if you don't like this prefix, you can always change it with \`prefix\` command!`)
    .addField(`**Moderation System :shield:**`, `If you would like to use moderation commands, such as \`jail\`, \`ban\`, \`kick\` and so much more... please run the \`setme\` command to quickly set up the moderation system.`)
    .addField(`**Support Server**`, `[Support Server](https://discord.gg/E5vPHzFU2S)`, true)
    .addField(`**Invite Bleed**`, `[Invite Here](https://discord.com/api/oauth2/authorize?client_id=868297144480710756&permissions=8&scope=bot)`, true)
    .addField(`**Upvote Bleed**`, `[Upvote Here](https://top.gg/bot/868297144480710756)`, true)

  if (!channelToSend) return;

  channelToSend.send(embed)
})