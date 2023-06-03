const { EmbedBuilder, ActionRowBuilder, ButtonBuilder } = require('discord.js')

const Command = require('../../Structures/Base/Command.js')

module.exports = class VoiceMaster extends Command {
    constructor (Client) {
        super (Client, 'voicemaster', {
            Aliases : [ '' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const Command = String(Arguments[0]).toLowerCase()

        if (!Arguments[0] || !['setup'].includes(Command)) {
            return new Client.Help(
                Message, {

                }
            )
        }

        switch (Command) {
            case ('setup') : {
                if (!Message.member.permissions.has('ManageGuild')) {
                    return new Client.Embed(
                        Message, `Permission **Manage Guild** is required to perform this command.`
                    )
                }

                Client.Database.query('SELECT * FROM voicemasters WHERE guild_id = $1', { bind : [ Message.guild.id ] }).then(async ([Results]) => {
                    if (Results.length > 0) {
                        return new Client.Response(
                            Message, `Cannot set up, **VoiceMaster** has already been set - Reset with \`voicemaster reset\``
                        )
                    }
                    
                    try {
                        const Category = await Message.guild.channels.create({ name : 'Voice Channels', type: 4 })
                        const JoinToCreate = await Message.guild.channels.create({ name : 'Join to Create', type: 2, parent: Category.id })

                        const Interface = await Message.guild.channels.create({ name : 'interface', type : 0, parent : Category.id })

                        Interface.permissionOverwrites.edit(Message.guild.roles.cache.find((Role) => Role.name.toLowerCase().trim() === '@everyone'), { 
                            SendMessages : false, 
                            AddReactions : false,
                            CreatePrivateThreads : false,
                            CreatePublicThreads : false
                        })

                        Client.Database.query('INSERT INTO voicemasters (guild_id, join_to_create, interface, category, default_category) VALUES ($1, $2, $3, $4, $5)', {
                            bind : [ Message.guild.id, JoinToCreate.id, Interface.id, Category.id, Category.id ]
                        })

                        return new Client.Response(
                            Message, `Set up **VoiceMaster** channels, bound to <#${JoinToCreate.id}>`
                        )
                    } catch (Error) {
                        return new Client.Error(
                            Message, 'voicemaster setup', Error
                        )
                    }
                })
            }
        }
    }
}