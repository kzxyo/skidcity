const fs = require('fs');
const { MessageEmbed, Permissions } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const notesFilePath = '/root/rewrite/Database/Users/notes.json';

module.exports = {
    configuration: {
        commandName: 'note',
        aliases: ['none'],
        description: 'Add or view notes for users in the guild',
        syntax: 'note <subcommand> (args)',
        example: 'note add @x6l garbage',
        module: 'utility',
        subcommands: ['> note add\n> note view\n> note remove'],
        permissions: 'manage_guild',
        parameters: 'user, note',
    },
    run: async (session, message, args) => {
        const [action, userArg, ...note] = args;
        const userID = userArg ? userArg.replace(/[<@!>]/g, '') : '';
        const guildID = message.guild.id;
        let notesData = JSON.parse(fs.readFileSync(notesFilePath, 'utf8'));
        const userNotes = notesData[guildID]?.[userID]?.notes || [];

        const noteText = note.join(' ');

        if (!action || !userArg) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            notesData[guildID] = notesData[guildID] || {};
            notesData[guildID][userID] = notesData[guildID][userID] || { notes: [] };

            switch (action) {
                case 'add': {
                    if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                                    .setColor(session.warn)
                            ]
                        });
                    }

                    if (!noteText) {
                        return displayCommandInfo(module.exports, session, message);
                    }

                    notesData[guildID][userID].notes.push(noteText);
                    fs.writeFileSync(notesFilePath, JSON.stringify(notesData, null, 2));

                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: Note added for <@${userID}>`)
                        ]
                    });
                }
                case 'view': {
                    const user = message.guild.members.cache.get(userID)?.user;
                    const username = user ? user.username : 'Unknown';

                    if (userNotes.length === 0) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor(session.warn)
                                    .setDescription(`${session.mark} ${message.author}: No notes found for ${username}`)
                            ]
                        });
                    }

                    const embed = new MessageEmbed()
                        .setColor(session.color)
                        .setTitle(`Notes for ${username}`)
                        .setDescription(userNotes.map((note, index) => `\`${index + 1}.\` ${note}`).join('\n'));

                    return message.channel.send({ embeds: [embed] });
                }
                case 'remove': {
                    if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_messages\``)
                                    .setColor(session.warn)
                            ]
                        });
                    }

                    if (!noteText || isNaN(parseInt(noteText))) {
                        return displayCommandInfo(module.exports, session, message);
                    }

                    const noteIndex = parseInt(noteText) - 1;
                    if (noteIndex < 0 || noteIndex >= userNotes.length) {
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setColor(session.warn)
                                    .setDescription(`${session.mark} ${message.author}: Invalid note index.`)
                            ]
                        });
                    }

                    const removedNote = notesData[guildID][userID].notes.splice(noteIndex, 1)[0];
                    fs.writeFileSync(notesFilePath, JSON.stringify(notesData, null, 2));

                    return message.channel.send({
                        embeds: [
                            new MessageEmbed()
                                .setColor(session.green)
                                .setDescription(`${session.grant} ${message.author}: Note removed for <@${userID}>: ${removedNote}`)
                        ]
                    });
                }
                default:
                    return displayCommandInfo(module.exports, session, message);
            }
        } catch (error) {
            session.log('Error:', error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.error)
                        .setDescription(`${session.mark} ${message.author}: An error occurred while processing the command.`)
                ]
            });
        }
    }
};
