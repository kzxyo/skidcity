const db = require('quick.db')
module.exports = async (client, message) => {
  if (message.partial) await message.fetch();
  if (!message.guild || message.channel.type === "dm") return;
    db.set(`Snipes_${message.guild.id}`, { 
      author: message.author, 
      message: message, 
      attachments: message.attachments.first() ? message.attachments.first() : null, 
      embed: message.embeds.length ? message.embeds[0] : null,
      time: Date.now()
    })

}
