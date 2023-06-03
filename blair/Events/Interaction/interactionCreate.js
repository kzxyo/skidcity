const Event = require('../../Structures/Base/Event.js')
const { EmbedBuilder, ChannelType, PermissionFlagsBits } = require('discord.js')
const { ActionRowBuilder } = require('discord.js')
const { ButtonBuilder } = require('discord.js')
const { Message } = require('discord.js')

module.exports = class InteractionCreate extends Event {
    constructor (Client) {
        super (Client, 'interactionCreate')
    }

    async Invoke (Interaction) {
        if (Interaction.isButton()) {
            if (Interaction.customId === 'TicketCreate') {
                await Interaction.deferUpdate()

                if (Interaction.guild.channels.cache.find((Channel) => Channel.topic === Interaction.user.id)) {
                    return Interaction.followUp({
                        embeds : [
                            new EmbedBuilder({
                                description : 'Maximum amount of **Tickets** you are allowed to have open has been reached.'
                            }).setColor(this.Client.Color)
                        ],
                        ephemeral : true
                    })
                }

                Interaction.guild.channels.create({
                    name : `ticket-${Interaction.user.username}`,
                    parent : '1052513249729454090',
                    topic : Interaction.user.id,
                    permissionOverwrites : [
                        {
                            id : Interaction.user.id,
                            allow : [PermissionFlagsBits.SendMessages, PermissionFlagsBits.ViewChannel]
                        },
                        {
                            id : '1052851124085989416',
                            allow : [PermissionFlagsBits.SendMessages, PermissionFlagsBits.ViewChannel]
                        },
                        {
                            id : '1052851212606775296',
                            allow : [PermissionFlagsBits.SendMessages, PermissionFlagsBits.ViewChannel]
                        },
                        {
                            id : '1029986260393136168',
                            deny : [PermissionFlagsBits.SendMessages, PermissionFlagsBits.ViewChannel]
                        }
                    ],
                    type : ChannelType.GuildText
                }).then(async (Ticket) => {
                    Interaction.followUp({
                        embeds : [
                            new EmbedBuilder({
                                description : `Created <#${Ticket.id}> - Provide a **Server ID** and **Invite**!`
                            }).setColor(this.Client.Color)
                        ],
                        ephemeral : true
                    })

                    Ticket.send({
                        content : `<@${Interaction.user.id}> <@&1052851212606775296>`,
                        embeds : [
                            new EmbedBuilder({
                                author : {
                                    name : `${Interaction.user.username}`,
                                    iconURL : Interaction.user.displayAvatarURL({
                                        dynamic : true
                                    })
                                },
                                description : 'Staff will be with you in a few minutes.\nPlease explain what you need in the meantime.'
                            }).setColor(this.Client.Color)
                        ],
                        components : [
                            new ActionRowBuilder().addComponents(
                                new ButtonBuilder({
                                    label : 'Close',
                                    emoji : '🔒',
                                    customId : 'TicketClose'
                                }).setStyle('Secondary'),
                                new ButtonBuilder({
                                    label : 'Claim',
                                    emoji : '✅',
                                    customId : 'TicketClaim',
                                    disabled : true
                                }).setStyle('Secondary')
                            )
                        ]
                    })
                })
            } else if (Interaction.customId === 'TicketClose') {
                await Interaction.deferUpdate()
                
                if (((Interaction.channel.topic === Interaction.user.id)) === Interaction.user.id && '1052851212606775296' !== Interaction.user.id) {
                    return
                }

                const Member = await Interaction.guild.members.cache.get(Interaction.channel.topic)
                
                Interaction.channel.edit({
                    name : `closed-${Member.user.username}`,
                    parent : '1052522113816330240',
                    topic : 'Closed Ticket',
                    permissionOverwrites : [
                        {
                            id : Interaction.channel.topic,
                            deny : [PermissionFlagsBits.SendMessages, PermissionFlagsBits.ViewChannel]
                        },
                        {
                            id : '1052851124085989416',
                            allow : [PermissionFlagsBits.SendMessages, PermissionFlagsBits.ViewChannel]
                        },
                        {
                            id : '1029986260393136168',
                            deny : [PermissionFlagsBits.SendMessages, PermissionFlagsBits.ViewChannel]
                        }
                    ],
                    type : ChannelType.GuildText
                })
            }
        }        
    }
}