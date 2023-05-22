const Subcommand = require('../../Subcommand.js');
const db = require('quick.db');
const { MessageEmbed } = require('discord.js');

module.exports = class check extends Subcommand {
  constructor(client) {
    super(client, {
      base: 'vanityrole',
      name: 'check',
      type: client.types.SERVER,
      usage: 'vanityrole check',
      description: 'Check your vanityrole settings',
    });
  }
  async run(message, args) {
    const check = await message.client.db.vanity_status.findOne({where: {guildID: message.guild.id}})
    const role = await  message.client.db.vanity_role.findOne({where: {guildID: message.guild.id}})
    const channel = await  message.client.db.vanity_channel.findOne({where: {guildID: message.guild.id}})
    const msg = await  message.client.db.vanity_message.findOne({where: {guildID: message.guild.id}})
    const embed = new MessageEmbed()
      .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
      .setColor(this.hex)
      .setFooter(`Watching ${message.guild.memberCount} members`)
      .setDescription(`> Vanity roles are **${check !== null ? 'on' : 'off'}**\n${check ? `> Watching for **${check.status}**` : ''}`)
      .addField(`Role`, `${role ? message.guild.roles.cache.get(role.role) : 'None'}`, true)
      .addField(`Channel`, `${channel ? message.guild.channels.cache.get(channel.channel) : 'None'}`, true)
      .addField(`Message`, `${msg ? msg.message : 'None'}`, true)
    message.channel.send({ embeds: [embed] })
  }
}