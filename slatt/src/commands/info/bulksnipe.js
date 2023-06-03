const Command = require('../Command.js');
const db = require(`quick.db`)
const Discord = require('discord.js')
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class BulkSnipeCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'bulksnipe',
      aliases: ['bs', 'bulks', 'purgesnipe'],
      subcommands: [`bulksnipe`],
      description: `Snipe multiple purged messages`,
      type: client.types.INFO,
    });
  }
  async run(message) {
    const snipe = db.get(`BulkSnipe_${message.guild.id}`)
    if(!snipe) return this.send_info(message, `There were no recently purged messages`)
    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.tag, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle(`Purge Snipe`)
      .setDescription(snipe.join('\n'))
      .setFooter(`Sniped by: ${message.author.tag}`)
      .setColor(this.hex)
      .setTimestamp()
      if (snipe.length <= 10) {
        const range = (snipe.length == 1) ? '[1]' : `[1 - ${snipe.length}]`;
        message.channel.send({ embeds: [embed] });
      } else {
        new ReactionMenu(message.client, message.channel, message.member, embed, snipe);
      }
  }
}