//const { MessageEmbed } = require('discord.js')
const { EmbedBuilder } = require('../../utils/embedbuilder')

module.exports = {
  name: "testembed",
  description: `reloads all commands (dev only)`,
  usage: '{guildprefix}reload',
  run: async(client, message, args) => {

    if (message.author.id !== '1114247260474196098') return;
  }
}