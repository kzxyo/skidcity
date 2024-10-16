const { Permissions } = require("discord.js");

module.exports = {
  name: "cleanup",
  description: `clean up bot and invoking messages`,
  usage: '{guildprefix}cleanup',
  run: async(client, message, args) => {

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires \`manage messages\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires me to have \`manage messages\` permission`)

    const number = args[0]

    if(isNaN(number)) return message.channel.send('you need to input a number')

    if(number < 1) return message.channel.send('provide a number above 1')

    if(number > 99) return message.channel.send('provide a number less than 99')
  
    let messages = await message.channel.messages.fetch({ limit: number })
    let filteredmessages = await messages.filter(x => x.author.bot)

    if (filteredmessages.size === 0) {

      return message.channel.send('no messages found from bots').then((msg) => {
        setTimeout(() => msg.delete().catch(() => { return; }), 3000);
      })
    
    } else {

      message.channel.bulkDelete(filteredmessages, true).then(() => {
        return message.channel.send('cleaned up 👍')    .then((msg) => {
          setTimeout(() => msg.delete().catch(() => { return; }), 3000);
        }) 
      }).catch(() => {
        return message.channel.send('an error occured')     
      })
    }
  }
}