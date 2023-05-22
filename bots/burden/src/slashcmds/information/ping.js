module.exports = {
  name: "ping",
  description: "returns bot's ping",
  type: 'CHAT_INPUT',
  run: async (client, interaction, args) => {
    await interaction.followUp({ content: `${client.ws.ping}ms` });
  },
};