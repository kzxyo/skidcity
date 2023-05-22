const { MessageEmbed } = require('discord.js')
function Embed(msg) {
    return new MessageEmbed()
        .setColor('#303135')
        .setAuthor(msg.author.tag, msg.author.avatarURL({ dynamic: true }))
        
}

module.exports = Embed