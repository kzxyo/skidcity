const fetch = require('node-fetch');

module.exports = {
  name: "yomama",
  aliases: ['ym', 'yomomma'],
  description: `sends a random yo mama joke`,
  usage: '{guildprefix}yomama',
  run: async(client, message, args) => {

    const res = await fetch('https://api.yomomma.info');
    let joke = (await res.json()).joke;

    message.channel.send({ content: joke })
  }
}