const { joinVoiceChannel, createAudioPlayer, createAudioResource } = require('@discordjs/voice');
const { MessageEmbed } = require('discord.js');

module.exports = {
    configuration: {
        commandName: 'esex',
        aliases: ['none'],
        description: 'Get down and dirty with the bot',
        syntax: 'esex',
        example: 'esex',
        module: 'fun'
    },
    run: async (session, message) => {
        
        const member = message.member;
        if (!member || !member.voice.channel) {
            return message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: You're not in a **voice channel** :wink:`)
            ]});
        }

        try {
            const channel = joinVoiceChannel({
                channelId: member.voice.channelId,
                guildId: member.guild.id,
                adapterCreator: member.guild.voiceAdapterCreator,
            });

            const player = createAudioPlayer();
            const resource = createAudioResource('/root/rewrite/Utils/esex.mp3');

            player.play(resource);
            channel.subscribe(player);

            player.on('stateChange', (oldState, newState) => {
                if (newState.status === 'idle') {
                    channel.connection.destroy();
                    message.channel.send('I finished daddy-waddy ^_^');
                }
            });
        } catch (error) {
            console.error('Error playing audio:', error);
            message.channel.send('An error occurred while playing audio.');
        }
    }
};
