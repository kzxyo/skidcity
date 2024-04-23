const fs = require('fs').promises;

module.exports = {
    configuration: {
        eventName: 'messageUpdate',
        devOnly: false
    },
    run: async (session, oldMessage, newMessage) => {
        if (!session.editsnipes) {
            session.editsnipes = new Map();
        }

        let editsnipes = session.editsnipes.get(newMessage.channel.id) || [];
        if (editsnipes.length > 20) editsnipes = editsnipes.slice(0, 19);

        editsnipes.unshift({
            oldMessage: oldMessage,
            newMessage: newMessage
        });

        session.editsnipes.set(newMessage.channel.id, editsnipes);
        let prefixes = {};
        try {
            const data = await fs.readFile('/root/rewrite/Database/Settings/prefix.json');
            prefixes = JSON.parse(data);
        } catch (error) {
            console.error('Error loading prefixes:', error);
        }

        let prefix = session.prefix;
        if (newMessage.guild && prefixes[newMessage.guild.id]) {
            const guildPrefixes = prefixes[newMessage.guild.id];
            if (guildPrefixes && guildPrefixes.length > 0) {
                for (const guildPrefix of guildPrefixes) {
                    if (newMessage.content.startsWith(guildPrefix)) {
                        prefix = guildPrefix;
                        break;
                    }
                }
            }
        }
        if (newMessage.content.startsWith(prefix)) {
            const args = newMessage.content.slice(prefix.length).trim().split(/ +/);
            const commandName = args.shift().toLowerCase();
            const command = session.commands.get(commandName) || session.commands.find(cmd => cmd.configuration.aliases && cmd.configuration.aliases.includes(commandName));

            if (command) {
                try {
                    session.log('Commands:', `${newMessage.author.username} updated message to command '${commandName}' in ${newMessage.guild ? newMessage.guild.name : 'DM'} (${newMessage.channel.id})`);
                    command.run(session, newMessage, args);
                } catch (error) {
                    newMessage.channel.send({
                        embeds: [
                            {
                                color: session.warn,
                                description: `${session.mark} ${newMessage.author}: An error occurred while executing the command`
                            }
                        ]
                    })
                }
            }
        }
    }
};
