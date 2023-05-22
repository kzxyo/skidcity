const { Client, CommandInteraction } = require("discord.js");
const db = require('../../core/db.js');

module.exports = {
  name: "whitelist",
  description: "whitelist a user",
  options: [
    {
      name: 'user',
      description: 'the user to whitelist',
      type: "USER",
      required: true
    }
  ],
  type: 'CHAT_INPUT',
  run: async (client, interaction, args) => {
    if (interaction.user.id === interaction.guild.ownerId) {
    const [userId] = args;
    const isWhitelisted = await db.get(`${interaction.guild.id}_wl_${userId}`);
    if (!isWhitelisted) {
      await db.set(`${interaction.guild.id}_wl_${userId}`, true);
      await interaction.followUp({
        content: `whitelisted that user successfully.`,
        ephemeral: true
      })
    } else {
      await interaction.followUp({
        content: `that user is already whitelisted.`,
        ephemeral: true
      })
    }
    } else {
      await interaction.reply({
        content: 'This command is for the server owner'
      })
    }
  },
};