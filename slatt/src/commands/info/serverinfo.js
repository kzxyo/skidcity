const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');
const moment = require('moment');
const Discord = require('discord.js');
const { stripIndent } = require('common-tags');

module.exports = class ServerInfoCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'serverinfo',
      aliases: ['server', 'si'],
      usage: 'serverinfo',
      subcommands: ['serverinfo'],
      description: 'Fetches information and statistics about the server.',
      type: client.types.INFO
    });
  }
  async run(message, args) {
    let row = new Discord.MessageActionRow()
    if (message.guild.bannerURL()) {
      row.addComponents(new Discord.MessageButton()
        .setURL(message.guild.bannerURL())
        .setLabel(`Banner URL`)
        .setStyle(`LINK`)
        .setEmoji(`🔗`))
    }
    if (message.guild.iconURL()) {
      row.addComponents(new Discord.MessageButton()
        .setURL(message.guild.iconURL({ dynamic: true }) || 'https://cdn.discordapp.com/emojis/828538929979588648.png?v=1')
        .setLabel(`Icon URL`)
        .setStyle(`LINK`)
        .setEmoji(`🔗`))
    }
    const Users = await message.client.db.LastfmUsers.findAll()
    const embed = new MessageEmbed()
      .setColor(this.hex)
      .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
      .setTitle(`${message.guild.name} ${message.guild.vanityURLCode ? `/${message.guild.vanityURLCode}` : ''}`)
      .setDescription(stripIndent`
      ${message.client.emotes.mod} Owner ${message.guild.members.cache.get(message.guild.ownerId)}
      ${message.client.emotes.server} Server created **${moment(message.guild.createdAt).format("MM/DD/YY")}**
      ${message.client.emotes.nitro} Boost count **${message.guild.premiumSubscriptionCount}** 
      ${message.guild.description ? `${message.client.emotes.info} *${message.guild.description}*` : ''}
        `)
      .addField(`Channels`, `${message.guild.channels.cache.size}`, true)
      .addField(`Roles`, `${message.guild.roles.cache.size}`, true)
      .addField(`Members`, `${message.guild.memberCount}`, true)
      .addField(`Stickers`, `${message.guild.stickers.cache.size}`, true)
      .addField(`Emojis`, `${message.guild.emojis.cache.size}`, true)
      .addField(`Last.fm users`, `${Users.filter(x => message.guild.members.cache.get(x.userID)).length}`, true)
      .setThumbnail(message.guild.iconURL({ dynamic: true }))
      .setFooter(`I joined this server on ${moment(message.guild.joinedAt).format("MM/DD/YY")}`)
    message.channel.send({ embeds: [embed], components: [row] })
  }
};