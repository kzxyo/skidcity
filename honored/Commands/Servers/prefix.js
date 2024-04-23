const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const database = require('/root/rewrite/Database/Settings/prefix.json');
const fs = require('fs');

module.exports = {
    configuration: {
        commandName: 'prefix',
        description: 'Change the prefix for the server',
        syntax: 'prefix <subcommands> (args)',
        example: 'prefix add !',
        permissions: 'manage_guild',
        aliases: ['setprefix'],
        subcommands: ['> prefix add\n> prefix list\n> prefix remove\n> prefix clear'],
        module: 'servers'
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has('MANAGE_GUILD')) {

            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                ]
            });
        }
        const guildID = message.guild.id;
        const guildPrefixes = database[guildID] || [];
        
        const subcommand = args[0];
        const prefix = args[1];

        switch (subcommand) {
            case 'add':
                if (!prefix || prefix.length < 1 || guildPrefixes.length >= 4) {
                    return message.channel.send({ embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: Prefix must be at least 1 character and you can only have 4 prefixes`)
                    ]});
                }

                if (guildPrefixes.includes(prefix)) {
                    return message.channel.send('This prefix already exists for this server.');
                }

                guildPrefixes.push(prefix);
                database[guildID] = guildPrefixes;
                fs.writeFileSync('/root/rewrite/Database/Settings/prefix.json', JSON.stringify(database, null, 4));
                message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: Prefix \`${prefix}\` added successfully`)
                ]});
                break;

            case 'list':
                const embed = new MessageEmbed()
                    .setColor(session.color)
                    .setAuthor(message.guild.name, message.guild.iconURL({ dynamic: true }))
                    .setTitle('Prefixes for this server')
                    .setDescription(guildPrefixes.length > 0 ? guildPrefixes.map(p => `\`${p}\``).join(', ') : '/');
                message.channel.send({ embeds: [embed] });
                break;

            case 'remove':
                if (!prefix || !guildPrefixes.includes(prefix)) {
                    return message.channel.send({ embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: Prefix \`${prefix}\` doesn't exist for this server`)
                    ]});
                }

                const updatedPrefixes = guildPrefixes.filter(p => p !== prefix);
                database[guildID] = updatedPrefixes;
                fs.writeFileSync('/root/rewrite/Database/Settings/prefix.json', JSON.stringify(database, null, 4));
                message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: Prefix \`${prefix}\` removed successfully.`)
                ]});
                break;

            case 'clear':
                if (guildPrefixes.length === 0) {
                    return message.channel.send({ embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: No prefixes set for this server`)
                    ]});
                }

                delete database[guildID];
                fs.writeFileSync('/root/rewrite/Database/Settings/prefix.json', JSON.stringify(database, null, 4));
                message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.green)
                        .setDescription(`${session.grant} ${message.author}: Prefixes cleared successfully`)
                ]});
                break;

            default:
                displayCommandInfo(module.exports, session, message);
                break;
        }
    }
};
