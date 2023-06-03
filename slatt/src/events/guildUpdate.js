const db = require('quick.db')
const Discord = require('discord.js')
module.exports = (client, oldGuild, newGuild) => {
  if (oldGuild.name == newGuild.name) return;
  client.logger.info(`${oldGuild.name} server name changed to ${newGuild.name}`);
};