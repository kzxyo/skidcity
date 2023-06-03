const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');
const moment = require('moment');
const Discord = require('discord.js');
const {stripIndent} = require('common-tags')
module.exports = class BotInfoCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'botinfo',
      aliases: ['bi', 'about', 'info'],
      subcommands: ['botinfo'],
      usage: 'botinfo',
      description: 'Slart',
      type: client.types.INFO
    });
  }
  async run(message) {
    const botOwner = message.client.users.cache.get('540071388069756931')
    const d = moment.duration(message.client.uptime);
    const date = moment().subtract(d, 'ms').format('dddd, MMMM Do YYYY')
    let row = new Discord.MessageActionRow()
    row.addComponents(new Discord.MessageButton()
      .setURL(`https://discord.com/api/oauth2/authorize?client_id=${message.client.user.id}&permissions=8&scope=bot`)
      .setLabel(`Invite`)
      .setStyle(`LINK`)
      .setEmoji(`${message.client.emotes.info}`))
    row.addComponents(new Discord.MessageButton()
      .setURL('https://slatt.gay/commands')
      .setLabel(`Commands`)
      .setStyle(`LINK`)
      .setEmoji(`${message.client.emotes.mod}`))
    row.addComponents(new Discord.MessageButton()
      .setURL('https://commands.slatt.gay/bot/recent-updates')
      .setLabel(`Updates`)
      .setStyle(`LINK`)
      .setEmoji(`${message.client.emotes.search}`))

    const embed = new MessageEmbed()
      .setColor(this.hex)
      .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
      .setTitle(`${message.client.user.username}`)
      .setDescription(`*re-written in v.13*`)
      .addField(`🗒️ prefix`, `${message.prefix}`, true)
      .addField(`${message.client.emotes.server} ID`, `${message.client.user.id}`, true)
      .addField(`${message.client.emotes.dev} Owner`, `Narly`, true)
      .addField(`More info`, stripIndent`
      Servers **${message.client.guilds.cache.size}**
      Commands: **${parseInt(message.client.commands.size) + parseInt(message.client.subcommands.size)}** (${message.client.aliases.size} aliases)
      Up since: **${date}**
      `)
      .setThumbnail(message.client.user.avatarURL())
      .setFooter(`Created on ${moment(message.client.user.createdAt).format('MM/DD/YY')}`)
    message.channel.send({ embeds: [embed], components: [row] });
  }
};