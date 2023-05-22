const Command = require('../Command.js');
const fetch = require('node-fetch');
const { MessageEmbed } = require('discord.js');

module.exports = class CatCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'cat',
      aliases: ['kitten', 'kitty'],
      usage: 'cat',
      description: 'return random cat images',
      type: client.types.FUN
    });
  }
  async run(message) {
    fetch('https://api.thecatapi.com/v1/images/search').then(response => response.json()).then(res => {
      if (!res || !res[0]) {
        return this.api_error(message, 'random cat')
      }
      const embed = new MessageEmbed()
        .setColor(this.hex)
        .setTitle(':cat:')
        .setImage(res[0].url)
      message.channel.send({ embeds: [embed] })
    })
  }
};