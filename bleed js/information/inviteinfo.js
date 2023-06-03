const Discord = require('discord.js');
const moment = require('moment');
const { color } = require("../../config.json");
const { warn } = require("../../emojis.json");

module.exports = {
  name: "inviteinfo",

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: inviteinfo')
      .setDescription('View basic invite code information')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'code', true)
      .addField('**Information**', `N/A`, true)
      .addField('**Usage**', '\`\`\`Syntax: inviteinfo (code)\nExample: inviteinfo four\`\`\`')
      .setFooter(`Module: information`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(embed)

    const guild = await client.guilds.fetch(client.guilds.resolveID(mentionedMember)).catch(() => null);
    if (!guild) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Invalid **invite code** given` } })

    let banner = guild.bannerURL({ dynamic: true, format: "png", size: 2048 })
    if (banner) {
      banner = `[**Banner Image**](${guild.bannerURL({ dynamic: true, format: "png", size: 2048 })})`
    } else {
      banner = ''
    }

    let splash = guild.splashURL({ dynamic: true, format: "png", size: 2048 })
    if (splash) {
      splash = `[**Splash Image**](${guild.splashURL({ dynamic: true, format: "png", size: 2048 })})`
    } else {
      splash = ''
    }

    let icon = guild.iconURL({ dynamic: true, format: "png", size: 2048 })
    if (icon) {
      icon = `[**Icon Image**](${guild.iconURL({ dynamic: true, format: "png", size: 2048 })})`
    } else {
      icon = ''
    }

    let rulesChannel = guild.rulesChannel.name
    if (rulesChannel) {
      rulesChannel = `${guild.rulesChannel.name} (\`${guild.rulesChannel.type}\`)`
    } else {
      rulesChannel = 'N/A'
    }

    let rulesChannelid = guild.rulesChannel
    if (rulesChannelid) {
      rulesChannelid = `\`${guild.rulesChannel.id}\``
    } else {
      rulesChannelid = 'N/A'
    }

    let rulesChannelCreated = guild.rulesChannel
    if (rulesChannelCreated) {
      rulesChannelCreated = `${moment(guild.rulesChannel.createdAt).format("dddd, MMMM Do YYYY, h:mm A")}`
    } else {
      rulesChannelCreated = 'N/A'
    }

    const verificationLevels = {
      NONE: 'None',
      LOW: 'Low',
      MEDIUM: 'Medium',
      HIGH: 'High',
      VERY_HIGH: 'Highest'
    };

    const inviteembed = new Discord.MessageEmbed()
      .setColor(mentionedMember.displayHexColor || color)
      .setAuthor(message.author.username, message.author.avatarURL({ dynamic: true }))
      .setTitle(`Invite Code: ${guild.id}`)
      .addField(`**Channel & Invite**`, `**Name:** ${rulesChannel}\n**ID:** ${rulesChannelid}\n**Created:** ${rulesChannelCreated}\n**Invite Expiration:** Never\n**Inviter:** Unknown\n**Temporary:** N/A\n**Usage:** N/A`, true)
      .addField(`**Guild**`, `**Name:** ${guild.name}\n**ID:** \`${guild.id}\`\n**Created:** ${moment(guild.createdAt).format("dddd, MMMM Do YYYY, h:mm A")}\n**Members:** ${guild.memberCount}\n**Members Online:** ${guild.approximatePresenceCount}\n**Verification Level:** ${verificationLevels[guild.verificationLevel]}`, true)
      .addField(`**Design**`, `${icon} ${banner} ${splash}`)
      .setThumbnail(guild.iconURL())
    message.channel.send(inviteembed);
  }
}