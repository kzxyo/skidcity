const fetch = require('node-fetch');

module.exports = {
  name: "advice",
  description: `sends a random piece of advice`,
  usage: '{guildprefix}advice',
  run: async(client, message, args) => {

    const data = await fetch('https://api.adviceslip.com/advice')
    .then(res => res.json())
    .catch(() => null)

    if (!data){
      return;
    };

    message.channel.send({ content: data.slip.advice })
  }
}