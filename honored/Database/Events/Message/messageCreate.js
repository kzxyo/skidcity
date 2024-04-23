const cooldowns = new Map();
const { MessageEmbed } = require('discord.js');
const fs = require('fs');

module.exports = {
    configuration: {
        eventName: 'messageCreate',
        devOnly: false
    },
    run: async (session, message) => {
        if (message.author.bot) return;
    
        let prefixes = {};
    
        try {
            prefixes = JSON.parse(fs.readFileSync('/root/rewrite/Database/Settings/prefix.json', 'utf8'));
        } catch (error) {
            console.error('Error loading prefixes:', error);
        }
    
        let prefix = session.prefix;
        if (message.guild && prefixes[message.guild.id]) {
            const guildPrefixes = prefixes[message.guild.id];
            if (guildPrefixes && guildPrefixes.length > 0) {
                for (const guildPrefix of guildPrefixes) {
                    if (message.content.startsWith(guildPrefix)) {
                        prefix = guildPrefix;
                        break;
                    }
                }
            }
        }
    
        if (!message.content.startsWith(prefix)) {
            return;
        }
    
        const args = message.content.slice(prefix.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();
        const command = session.commands.get(commandName) || session.commands.find(cmd => cmd.configuration.aliases && cmd.configuration.aliases.includes(commandName));
    
        if (!command) {
            return;
        }
    
        if (!cooldowns.has(commandName)) {
            cooldowns.set(commandName, new Map());
        }
        const now = Date.now();
        const timestamps = cooldowns.get(commandName);
        const cooldownAmount = 2000;
    
        if (timestamps.has(message.author.id)) {
            const expirationTime = timestamps.get(message.author.id) + cooldownAmount;
    
            if (now < expirationTime) {
                const timeLeft = (expirationTime - now) / 1000;
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: Please wait ${timeLeft.toFixed(1)}s before using another command`)
                    ]
                });
            }
        }
    
        timestamps.set(message.author.id, now);
        setTimeout(() => {
            timestamps.delete(message.author.id);
        }, cooldownAmount);
    
        try {
            message.channel.sendTyping();
    
            session.log('Commands:', `${message.author.username} used command '${commandName}' in ${message.guild ? message.guild.name : 'DM'} (${message.channel.id})`);
    
            await command.run(session, message, args);
        } catch (error) {
            console.error(error);
    
            message.channel.send({
                embeds: [
                    {
                        color: session.warn,
                        description: `${session.mark} ${message.author}: An error occurred while executing the command`
                    }
                ]
            }).catch(console.error);
        } finally {
        }
    }
};
