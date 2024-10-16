module.exports = {
  name: "coinflip",
  aliases: ['cf'],
  description: `flips a coin`,
  usage: '{guildprefix}coinflip',
  run: async(client, message, args) => {

    const answers = [
      'heads',
      'tails',
    ];
    
    const randomanswers = answers[Math.floor(Math.random() * answers.length)];
        
    message.channel.send('flipping a coin... <a:conflip1:1001562797408264302>').then(msg => {
      msg.edit(`it landed on **${randomanswers}** <:coinflip2:1001562813522788482>`)
    })
  }
}