const { MessageEmbed, Permissions } = require("discord.js");

module.exports = {
    configuration: {
        commandName: "disconnect",
        aliases: ["dc"],
        description: "Disconnect the bot from the voice channel.",
        syntax: 'disconnect',
        example: 'disconnect',
        permissions: 'N/A',
        parameters: 'N/A',
        module: "music"
    },
    run: async (session, message, args) => {

        const voiceChannel = message.member.voice.channel;
        if (!voiceChannel) {
        return message.channel.send({
            embeds: [
            new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: You must be in a voice channel`)
                .setColor(session.warn)
            ]
        });
        }
    
        const botVoiceChannel = message.guild.me.voice.channel;
        if (botVoiceChannel && botVoiceChannel !== voiceChannel) {
        return message.channel.send({
            embeds: [
            new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: You are not in my voice channel`)
                .setColor(session.warn)
            ]
        });
        }
    
        try {
        await session.player.stop(message);
        } catch (error) {
        session.log("Error:", error)
        message.channel.send({
            embeds: [
            new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: Error disconnecting from the voice channel. Please try again later.`)
                .setColor(session.warn)
            ]
        });
        }
    }
    }