module.exports = {
  name: "ping",
  aliases: ['ms', 'latency'],
  description: `gets bot ping`,
  usage: '{guildprefix}ping',
  run: async(client, message, args) => {
  
    message.channel.send(`websocket: **${Math.round(client.ws.ping)}ms**`).then(msg => {
      setTimeout(() => msg.edit(`websocket: **${Math.round(client.ws.ping)}ms** (${(Date.now() - message.createdTimestamp)})`).catch(() => { return; }), 3000);
    })
  }
}