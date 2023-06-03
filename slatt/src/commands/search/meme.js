const Command = require('../Command.js');
const { MessageEmbed } = require('discord.js');
const fetch = require('node-fetch');

module.exports = class MemeCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'meme',
      usage: 'meme',
      subcommands: ['meme'],
      description: 'Displays a random meme from the `memes`, `dankmemes`, or `me_irl` subreddits.',
      type: client.types.SEARCH,
    });
  }
  async run(message) {
    try {
      let res = await fetch('https://meme-api.herokuapp.com/gimme');
      res = await res.json();
      const embed = new MessageEmbed()
        .setTitle(res.title)
        .setImage(res.url)
        .setColor(this.hex);
      message.channel.send({ embeds: [embed] });
    } catch (err) {
      message.client.logger.error(err.stack);
      this.send_error(message, 1, 'Please try again in a few seconds', err.message);
    }
  }
};
