const Command = require('../Command.js');
const ReactionMenu = require('../ReactionMenu.js');
const {
  MessageEmbed
} = require('discord.js');

module.exports = class ServersCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'servers',
      aliases: ['servs'],
      usage: `servers`,
      description: 'Displays a list of Kami\'s joined servers.',
      type: client.types.OWNER,
      ownerOnly: true
    });
  }
  async run(message) {
    let num = 0
    const servers = message.client.guilds.cache.sort((a, b) => b.memberCount - a.memberCount).map(guild => `${++num} **${guild.name}** (${guild.memberCount.toLocaleString()}) - ${guild.members.cache.get(guild.ownerId).user.tag}`)

    const embed = new MessageEmbed()
      .setTitle('Servers')
      .setAuthor(message.member.user.tag, message.author.displayAvatarURL({
        dynamic: true
      }))
      .setDescription(servers.join('\n'))
      .setColor(this.hex);
    if (servers.length <= 10) {
      message.channel.send({ embeds: [embed] });
    } else {
      new ReactionMenu(message.client, message.channel, message.member, embed, servers);
    }
  }
};