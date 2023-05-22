const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class Setup extends Command {
    constructor (Client) {
        super (
            Client, 'setup', {
                Aliases : ['setme'],

                Permissions : ['Administrator']
            }
        )
    }

    async Invoke (Client, Message, Arguments) {
        try {
            const SettingsMessage = await Message.channel.send({
                embeds : [
                    new EmbedBuilder({
                        description: `Starting **Moderation System** setup.`
                    }).setColor(Client.Color)
                ]
            })

            Client.Database.query(`SELECT * FROM moderation_systems WHERE guild_id = ${Message.guild.id}`).then(async ([Results]) => {
                var Jail, Jailed, ModerationLog, Muted, ImageMuted, ReactionMuted

                try {    
                    if (Results.length === 0) {
                        const CreatedJail = await Message.guild.channels.create({ name : 'Jail', type : 0 })
                        const CreatedJailed = await Message.guild.roles.create({ name : 'Jailed', permissions : [] })
                        const CreatedModerationLog = await Message.guild.channels.create({ name : 'Blair Log', type : 0 })
                        const CreatedMuted = await Message.guild.roles.create({ name : 'Muted', permissions : [] })
                        const CreatedImageMuted = await Message.guild.roles.create({ name : 'Image Muted', permissions : [] })
                        const CreatedReactionMuted = await Message.guild.roles.create({ name : 'Reaction Muted', permissions : [] })
                        
                        Jail = CreatedJail, 
                        Jailed = CreatedJailed, 
                        ModerationLog = CreatedModerationLog,
                        Muted = CreatedMuted,
                        ImageMuted = CreatedImageMuted,
                        ReactionMuted = CreatedReactionMuted
                    }
                    
                    if (Results.length > 0) {
                        const FetchedJail = await Message.guild.channels.cache.get(Results[0].jail_id)
                        
                        if (FetchedJail) {
                            Jail = FetchedJail
                        } else {
                            const CreatedJail = await Message.guild.channels.create({ name : 'Jail', type : 0 })
                            
                            Jail = CreatedJail
                        }
                        
                        const FetchedJailed = await Message.guild.roles.cache.get(Results[0].jailed_id)
                        
                        if (FetchedJailed) {
                            Jailed = FetchedJailed
                        } else {
                            const CreatedJailed = await Message.guild.roles.create({ name : 'Jailed', permissions : [] })
                            
                            Jailed = CreatedJailed
                        }
                        
                        const FetchedModerationLog = await Message.guild.channels.cache.get(Results[0].modlog_id)
                        
                        if (FetchedModerationLog) {
                            ModerationLog = FetchedModerationLog
                        } else {
                            const CreatedModerationLog = await Message.guild.channels.create({ name : 'Blair Log', type : 0 }) 
                            
                            ModerationLog = CreatedModerationLog
                        }
                        
                        const FetchedMuted = await Message.guild.roles.cache.get(Results[0].muted_id)
                        
                        if (FetchedMuted) {
                            Muted = FetchedMuted
                        } else {
                            const CreatedMuted = await Message.guild.roles.create({ name : 'Muted', permissions : [] })
                            
                            Muted = CreatedMuted
                        }
                        
                        const FetchedImageMuted = await Message.guild.roles.cache.get(Results[0].imagemuted_id)
                        
                        if (FetchedImageMuted) {
                            ImageMuted = FetchedImageMuted
                        } else {
                            const CreatedImageMuted = await Message.guild.roles.create({ name : 'Image Muted', permissions : [] })
                            
                            ImageMuted = CreatedImageMuted
                        }
                        
                        const FetchedReactionMuted = await Message.guild.roles.cache.get(Results[0].reactionmuted_id)
                        
                        if (FetchedReactionMuted) {
                            ReactionMuted = FetchedReactionMuted
                        } else {
                            const CreatedReactionMuted = await Message.guild.roles.create({ name : 'Reaction Muted', permissions : [] })
                            
                            ReactionMuted = CreatedReactionMuted
                        }
                    }
                    
                    SettingsMessage.edit({
                        embeds : [
                            new EmbedBuilder({
                                description : `Setting up **Channel** and **Role** permissions.`
                            }).setColor(Client.Color)
                        ]
                    })
                    
                    await Jail.permissionOverwrites.edit(
                        Message.guild.roles.cache.find((Role) => String(Role.name).toLowerCase().trim() === '@everyone'), { 
                            ViewChannel : false
                        }
                    )

                    await ModerationLog.permissionOverwrites.edit(
                        Message.guild.roles.cache.find((Role) => String(Role.name).toLowerCase().trim() === '@everyone'), {
                            ViewChannel : false
                        }
                    )
    
                    Message.guild.channels.cache.forEach(async (Channel) => {
                        await Channel.permissionOverwrites.edit(
                            Message.guild.roles.cache.find((Role) => String(Role.id).trim() === Jailed.id), { 
                                ViewChannel : false
                            }
                        ).catch(() => {})  
                    })
    
                    await Jail.permissionOverwrites.edit(
                        Message.guild.roles.cache.find((Role) => String(Role.id).trim() === Jailed.id), { 
                            ViewChannel : true
                        }
                    )

                    if (Results.length > 0) {
                        Client.Database.query(`UPDATE moderation_systems SET jail_id = ${Jail.id}, jailed_id = ${Jailed.id}, modlog_id = ${ModerationLog.id}, muted_id = ${Muted.id}, imagemuted_id = ${ImageMuted.id}, reactionmuted_id = ${ReactionMuted.id} WHERE guild_id = ${Message.guild.id}`).catch((Error) => { 
                            console.error(Error) 
                        })
                    } else {
                        Client.Database.query(`INSERT INTO moderation_systems (guild_id, jail_id, jailed_id, modlog_id, muted_id, imagemuted_id, reactionmuted_id, jailroles) VALUES (${Message.guild.id}, ${Jail.id}, ${Jailed.id}, ${ModerationLog.id}, ${Muted.id}, ${ImageMuted.id}, ${ReactionMuted.id}, true)`).catch((Error) => {
                            console.error(Error)
                        })
                    }

                    SettingsMessage.edit({
                        embeds : [
                            new EmbedBuilder({
                                description : `Success, **Moderation System** setup has been completed.`
                            }).setColor(Client.Color)
                        ]
                    })
                } catch (Error) {
                    return console.error(Error)
                }
            })
        } catch (Error) {
            return console.error(Error)
        }
    }
}
