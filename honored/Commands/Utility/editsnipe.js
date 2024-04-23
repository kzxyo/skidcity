const { MessageEmbed } = require('discord.js');
const moment = require('moment');

module.exports = {
    configuration: {
        commandName: 'editsnipe',
        description: 'View recently edited messages in the current channel.',
        aliases: ['es'],
        syntax: 'editsnipe',
        example: 'editsnipe',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'utility',
        devOnly: false
    },
    run: async (session, message, args) => {
        const editsnipes = session.editsnipes.get(message.channel.id);
        
        if (!editsnipes || editsnipes.length === 0) {
            return message.channel.send({
                embeds: [new MessageEmbed().setColor('YELLOW').setDescription(`There are no recent message edits to display in this channel.`)]
            });
        }
        
        const latestEditsnipe = editsnipes[0];
        const embed = new MessageEmbed()
        .setColor(session.color)
        .setAuthor(latestEditsnipe.oldMessage.author.username, latestEditsnipe.oldMessage.author.displayAvatarURL({ dynamic: true }))
        .setDescription(`${latestEditsnipe.oldMessage.content} ( original )\n> ${latestEditsnipe.newMessage.content} ( edited )`)
        .setFooter(`Edited ${moment(latestEditsnipe.editedAt).fromNow()}`);
    
        
        message.channel.send({ embeds: [embed] });
    }
};
