module.exports = {
  name: "ping",
  aliases: ["latency"],

  run: async (client, message, args) => {
    let ping = [
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **your mother**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **the chinese government**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **lastfms ass computers**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **my teeshirt**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **lil mosey**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **north korea**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **localhost**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **twitter**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **the santos**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **the trash**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **a connection to the server**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **four on twitter**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **6ix9ines ankle monitor**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **fivem servers**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **new york**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **my black airforces**`,
      `it took \`${Math.round(client.ws.ping)}ms\` to ping **netflix database**`
    ];
    const random = Math.floor(Math.random() * ping.length);
    if (args[0] === "me") {
      message.reply(ping[random]);
    } else {
      message.channel.send(args.join(" ") + ping[random]);
    }
  }
}