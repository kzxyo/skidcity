const Command = require('../Command.js');
const Discord = require('discord.js')
module.exports = class Editsnipe extends Command {
  constructor(client) {
    super(client, {
      name: 'editsnipe',
      aliases: ['es'],
      subcommands: [`snipe`],
      description: `view a recently edited message`,
      type: client.types.FUN,
    });
  }
  async run(message) {
    let data = await message.client.db.editsnipes.findOne({where: {guildID: message.guild.id}})
    if (!data) {
      return this.send_error(message, 0, 'There was no recent **edited messages** found');
    }
    const embed = new Discord.MessageEmbed()
      .setTimestamp()
      .setAuthor(data.tag, data.avatar)
      .addField(`**Old Message**`, `${data.oldmsg}`)
      .addField(`**New Message**`, `${data.newmsg}`)
      .setFooter(`edit sniped by ${message.author.tag}`)
      .setColor(this.hex)
    message.channel.send({ embeds: [embed] });
  }
}