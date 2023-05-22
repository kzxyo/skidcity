const Command = require('../Command.js');
const db = require(`quick.db`)
const Discord = require('discord.js')
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class BulkSnipeCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'reactionhistory',
      aliases: ['rh', 'rhistory', 'reactionh'],
      subcommands: [`reactionhistory`],
      usage: 'reactionhistory [message_id]',
      description: `View recently added reactions of a message`,
      type: client.types.INFO,
    });
  }
  async run(message, args) {
    return message.channel.send('https://open.spotify.com/track/4OJgqyLQh5oM38PzThaqIp?si=4qEPlMWPSr-sPTnLZVqA_A')
    const messageID = args[0]
    if (isNaN(messageID)) return this.send_error(message, 1, `Provide a valid **message id**`)
    const check = this.db.get(`Reaction_History_${message.guild.id}`)
    if (!check) return this.send_error(message, 1, `There were no **recent reactions** added for ${messageID}`)
    let num = 1
    let list = check.filter(x => x.messageID === messageID).map(r => `\`${num++}\` Emoji: ${r.info.reaction} | **${r.info.author}**  (${r.info.time})`)
    if(!list.length) return this.send_error(message, 1, `There were no recent reactions for **${messageID}**`)
    const embed = new Discord.MessageEmbed()
      .setAuthor(message.author.tag, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle(`Reaction History`)
      .setDescription(list.join('\n'))
      .setColor(this.hex)
      .setFooter(`${list.length} current reactions`)
      .setTimestamp()
    if (list.length <= 10) {
      message.channel.send({ embeds: [embed] });
    } else {
      new ReactionMenu(message.client, message.channel, message.member, embed, list);
    }
  }
}