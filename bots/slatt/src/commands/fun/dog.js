const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');
const fetch = require('node-fetch');

module.exports = class DogCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'dog',
      aliases: ['puppy', 'pup'],
      usage: 'dog',
      subcommands: ['dog'],
      description: 'funny cute dog',
      type: client.types.FUN
    });
  }
  async run(message) {
    try {
      const res = await fetch('https://dog.ceo/api/breeds/image/random');
      const img = (await res.json()).message;
      const embed = new MessageEmbed()
        .setTitle('🐶')
        .setImage(img)
        .setColor(this.hex);
      message.channel.send({ embeds: [embed] });
    } catch (err) {
      message.client.logger.error(err.stack);
      this.send_error(message, 1, 'Please try again in a few seconds', err.message);
    }
  }
};