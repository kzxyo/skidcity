const Discord = require('discord.js');
const moment = require('moment');
const ms = require('ms');
const { color } = require("../../config.json");
const { verifiedServer } = require("../../emojis.json");

module.exports = {
  name: "serverinfo",
  aliases: ["si"],
  category: "information",

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    const botCount = message.guild.members.cache.filter(m => m.user.bot).size;
    const humanCount = message.guild.memberCount - botCount
    const { guild } = message
    const emojicount = message.guild.emojis.cache
    const roles = message.guild.roles.cache
    const create = `${moment(message.guild.createdAt).format("MMM Do YYYY")} (${ms(Date.now() - message.guild.createdAt, { long: true })})`

    let banner = message.guild.bannerURL({ dynamic: true, format: "png", size: 2048 })
    if (banner) {
      banner = `[Click Here](${message.guild.bannerURL({ dynamic: true, format: "png", size: 2048 })})`
    } else {
      banner = 'N/A'
    }

    let splash = message.guild.splashURL({ dynamic: true, format: "png", size: 2048 })
    if (splash) {
      splash = `[Click Here](${message.guild.splashURL({ dynamic: true, format: "png", size: 2048 })})`
    } else {
      splash = 'N/A'
    }

    let icon = message.guild.iconURL({ dynamic: true, format: "png", size: 2048 })
    if (icon) {
      icon = `[Click Here](${message.guild.iconURL({ dynamic: true, format: "png", size: 2048 })})`
    } else {
      icon = 'N/A'
    }

    let vanity = message.guild.vanityURLCode
    if (vanity) {
      vanity = `(discord.gg/${message.guild.vanityURLCode})`
    } else {
      vanity = ''
    }

    let features = [];

    guild.features.forEach(feature => {
      features.push(
        feature
          .toLowerCase()
          .replace(/(^|"|_)(\S)/g, (s) => s.toUpperCase())
          .replace(/_/g, " ")
          .replace(/Guild/g, "Server")
          .replace(/Use Vad/g, "Use Voice Acitvity")
      );
    });

    const verificationLevels = {
      NONE: 'None',
      LOW: 'Low',
      MEDIUM: 'Medium',
      HIGH: 'High',
      VERY_HIGH: 'Highest'
    };


    const embed = new Discord.MessageEmbed()
      .setColor(mentionedMember.displayHexColor || color)
      .setAuthor(`${message.author.username}`, message.author.displayAvatarURL({
        dynamic: true
      }))
      .setTitle(`${guild.name} ${vanity} ${message.guild.verified ? `${verifiedServer}` : ``}`)
      .setDescription(`Server created on __${create}__\n__${guild.name}__ is on bot shard ID: **${guild.shardID}/${guild.shardID}**`)
      .setThumbnail(message.guild.iconURL({
        dynamic: true,
        format: "png",
        size: 2048
      }))
      .setFooter(`Guild ID: ${guild.id}`)
      .setTimestamp()
      .addFields({
        name: "**Owner**",
        value: guild.owner.user.tag,
        inline: true,
      },
        {
          name: "**Members**",
          value: `**Total:** ${guild.memberCount}\n**Humans:** ${humanCount}\n**Bots:** ${botCount}`,
          inline: true,
        },
        {
          name: "**Information**",
          value: `**Region:** ${guild.region}\n**Verification:** ${verificationLevels[guild.verificationLevel]}\n**Level:** ${guild.premiumTier}/${guild.premiumSubscriptionCount} boosts`,
          inline: true,
        },
        {
          name: "**Design**",
          value: `**Banner:** ${banner}\n**Splash:** ${splash}\n**Icon:** ${icon}`,
          inline: true,
        },
        {
          name: `**Channels (${guild.channels.cache.size})**`,
          value: `**Text:** ${guild.channels.cache.filter(channel => channel.type == 'text').size}\n**Voice:** ${guild.channels.cache.filter(channel => channel.type == 'voice').size}\n**Category:** ${guild.channels.cache.filter(channel => channel.type == 'category').size}`,
          inline: true,
        },
        {
          name: "**Other**",
          value: `**Roles:** ${roles.size}/250\n**Emojis:** ${emojicount.size}/250`,
          inline: true,
        },
        {
          name: "**Features**",
          value: features.length
            ? features
              .map(feature => `\`${feature}\``)
              .join(", ")
            : "N/A",
          inline: true
        })

    message.channel.send(embed)
  }
}