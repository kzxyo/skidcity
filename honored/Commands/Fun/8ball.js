const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: '8ball',
        aliases: ['8b'],
        description: 'Ask the 8ball a question',
        syntax: '8ball <question>',
        example: '8ball am i cool?',
        module: 'fun',
        permissions: 'N/A',
        parameters: 'question'
    },

    run: async (client, message, args) => {
        if (!args[0]) 
            return displayCommandInfo(module.exports, client, message);

        const responses = [
            'Yes',
            'No',
            'Never',
            'Definitely',
            'Ask again later',
            'I am not sure',
            'Maybe',
            'It is certain',
            'Most likely',
            'I doubt it',
            'I don\'t think so',
            'I am not sure',
            'I don\'t know'
        ]

        const response = responses[Math.floor(Math.random() * responses.length)];

        const embed = new MessageEmbed()
            .setTitle('🎱 8ball')
            .setDescription(`**Question:** ${args.join(' ')}\n**Answer:** ${response}`)
            .setColor(session.color)
            .setTimestamp();

        message.channel.send({ embeds: [embed] });

    }

}