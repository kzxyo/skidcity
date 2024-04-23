module.exports = {
    configuration: {
        commandName: 'firstmessage',
        aliases: ['firstmsg'],
        description: 'Provides the first message of a channel.',
        syntax: 'firstmessage',
        example: 'firstmessage',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'information',
        devOnly: false
    },
    run: async (session, message, args) => {
        const guild = message.guild.id;
        const channel = message.channel.id;

        const fetchMessages = await message.channel.messages.fetch({
            after: 1,
            limit: 1,
        });
        const firstmessage = fetchMessages.first();

        const { MessageEmbed } = require("discord.js");

        const embed = new MessageEmbed()
        .setColor('#748cdc')
            .setDescription(`:mag: ${message.author}: The first message in ${message.channel} — **[jump](https://discord.com/channels/${guild}/${channel}/${firstmessage.id})**`);

        message.channel.send({ embeds: [embed] });
    }
};
