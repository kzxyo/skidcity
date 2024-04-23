const { MessageEmbed, Permissions } = require('discord.js');
const fs = require('fs');
const tagsPath = '/root/rewrite/Database/Settings/tags.json';
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'tags',
        aliases: ['t'],
        description: 'Manage tags',
        syntax: 'tags <subcommand> (args)',
        example: 'tags add meow kitty',
        module: 'servers',
        subcommands: ['> tags add\n> tags list\n> tags view\n> tags remove\n> tags reset']
    },
    run: async (session, message, args) => {
        if (!message.member.permissions.has('MANAGE_MESSAGES')) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                        .setColor(session.warn)
                ]
            });
        }

        const subcommand = args[0];
        if (subcommand === 'add') {
            const tag = args[1];
            const content = args.slice(2).join(' ');

            if (!tag || !content) {
                return displayCommandInfo(module.exports, session, message);
            }

            try {
                const guildTags = getGuildTags(message.guild.id);
                guildTags[tag] = content;
                saveGuildTags(message.guild.id, guildTags);

                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.grant} ${message.author}: Tag **${tag}** has been added.`)
                            .setColor(session.green)
                    ]
                });
            } catch (error) {
                console.error('Error adding tag:', error);
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: An error occured, please contact support`)
                            .setColor(session.warn)
                    ]
                });
            }
        } else if (subcommand === 'list') {
            const guildTags = getGuildTags(message.guild.id);
            const tagsList = Object.entries(guildTags).map(([tag, content]) => `${tag}: ${content}`).join('\n');

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`**Tags for ${message.guild.name}**\n${tagsList || 'No tags available'}`)
                        .setColor(session.color)
                ]
            });
        } else if (subcommand === 'view') {  
            const tagToView = args[1];

            if (!tagToView) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setTitle('Command: tags view')
                            .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                            .setDescription('View a tag```Syntax: tags view <tag>\nExample: tags view meow```')
                            .setColor(session.color)
                    ]
                });
            }

            const guildTags = getGuildTags(message.guild.id);
            const content = guildTags[tagToView];

            if (!content) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: Tag **${tagToView}** does not exist`)
                            .setColor(session.warn)
                    ]
                });
            }

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`**${tagToView}**\n${content}`)
                        .setColor(session.color)
                ]
            });
        } else if (subcommand === 'remove') {
            const tagToRemove = args[1];

            if (!tagToRemove) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setTitle('Command: tags remove')
                            .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                            .setDescription('Remove a tag```Syntax: tags remove <tag>\nExample: tags remove meow```')
                            .setColor(session.color)
                    ]
                });
            }

            try {
                const guildTags = getGuildTags(message.guild.id);
                if (!guildTags[tagToRemove]) {
                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setDescription(`${session.mark} ${message.author}: Tag **${tagToRemove}** does not exist`)
                                .setColor(session.warn)
                        ]
                    });
                }

                delete guildTags[tagToRemove];
                saveGuildTags(message.guild.id, guildTags);

                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.grant} ${message.author}: Tag **${tagToRemove}** has been removed`)
                            .setColor(session.green)
                    ]
                });
            } catch (error) {
                console.error('Error removing tag:', error);
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: An error occurred, please contact support`)
                            .setColor(session.warn)
                    ]
                });
            }
        } else if (subcommand === 'reset') {
            try {
                fs.writeFileSync(tagsPath, '{}');
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.grant} ${message.author}: Removed all existing tags for this server`)
                            .setColor(session.green)
                    ]
                });
            } catch (error) {
                console.error('Error resetting tags:', error);
                message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setDescription(`${session.mark} ${message.author}: An error occurred, please contact support`)
                            .setColor(session.warn)
                    ]
                });
            }
        } else {
            return displayCommandInfo(module.exports, session, message);
        }
    }
};

function getGuildTags(guildId) {
    try {
        const tagsData = fs.readFileSync(tagsPath, 'utf8');
        const allTags = JSON.parse(tagsData);
        return allTags[guildId] || {};
    } catch (error) {
        console.error('Error reading guild tags:', error);
        return {};
    }
}

function saveGuildTags(guildId, tags) {
    try {
        const allTags = JSON.parse(fs.readFileSync(tagsPath, 'utf8'));
        allTags[guildId] = tags;
        fs.writeFileSync(tagsPath, JSON.stringify(allTags, null, 4));
    } catch (error) {
        console.error('Error saving guild tags:', error);
    }
}
