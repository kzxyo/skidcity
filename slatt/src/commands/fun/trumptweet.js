const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');
const fetch = require('node-fetch');

module.exports = class TrumpTweetCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'trumptweet',
      aliases: ['trump'],
      usage: 'trumptweet <message>',
      description: 'Display\'s a custom tweet from Donald Trump with the message provided',
      type: client.types.FUN,
      subcommands: ['trumptweet trump is ugly']
    });
  }
  async run(message, args) {
    if (!args.length) {
      return this.help(message);
    }
    let tweet = message.content.slice(message.content.indexOf(args[0]), message.content.length);
    if (tweet.length > 68) tweet = tweet.slice(0, 65) + '...';

    try {
      const res = await fetch('https://nekobot.xyz/api/imagegen?type=trumptweet&text=' + tweet);
      const img = (await res.json()).message;
      const embed = new MessageEmbed()
        .setTitle('Fat Boy Trump')
        .setImage(img)
        .setColor(this.hex);
      message.channel.send({ embeds: [embed] });
    } catch (err) {
      message.client.logger.error(err.stack);
      this.send_error(message, 1, 'Please try again in a few seconds', err.message);
    }
  }
};