const { EmbedBuilder, ActionRowBuilder, ButtonBuilder } = require('discord.js')


module.exports = class Paginator {
    constructor (Message) {
        this.Message = Message
        this.Client = Message.client  
        this.Author = Message.author
        this.Member = Message.member

        this.Embeds = []

        this.Text = null
        this.Icon = null

        this.Seperator = false
        this.ShowEntries = false
        this.DisplayFirst = false
        this.DisplayFooter = false
        this.Entries = 0
    }

    async SetOptions (Options) {
        if (Options.Footer) {
            if (Options.Footer.Text) {
                this.Text = Options.Footer.Text
            }

            if (Options.Footer.IconURL) {
                this.Icon = Options.Footer.Icon
            }
        }

        if (Options.ShowEntries) {
            this.ShowEntries = true
        }

        if (Options.Seperator) {
            this.Seperator = true
        }

        if (Options.Entries) {
            this.Entries = parseInt(Options.Entries)
        }

        if (Options.DisplayFirst) {
            this.DisplayFirst = true
        }

        if (Options.DisplayFooter) {
            this.DisplayFooter = true
        }
    }

    async SetEmbeds (Embeds) {
        Embeds[0].setFooter({
            text : `Page 1/${Embeds.length}`,
            iconURL : this.Icon ? Icon : null
        })

        this.Embeds = Embeds
    }

    async Send () {
        const Embeds = this.Embeds

        const ActionRow = new ActionRowBuilder().addComponents(
            new ButtonBuilder({
                label : 'Previous',
                customId : 'Previous',
                emoji : '<:Previous:1052376922107162624>'
            }).setStyle('Secondary'),
            new ButtonBuilder({
                label : 'Next',
                customId : 'Next',
                emoji : '<:Next:1052376923793260574>'
            }).setStyle('Primary')
        )

        const iMessage = await this.Message.channel.send({
            embeds : [
                Embeds[0]
            ],
            components : [
                ActionRow
            ]
        })

        const Filter = async (Interaction) => {
            await Interaction.deferUpdate()

            if (Interaction.user.id !== this.Author.id) {
                this.Client.Response(
                    Interaction, `You don't own this embed!`, {
                        Ephemeral : true
                    }
                )
            }

            return Interaction.user.id === this.Author.id
        }

        const Collector = await iMessage.createMessageComponentCollector({
            Filter, time : 100000
        })

        var Index = 0

        Collector.on('collect', async (Interaction) => {
            await Interaction.deferUpdate()

            if (Interaction.user.id !== this.Author.id) {
                return
            }

            switch (Interaction.customId) {
                case ('Previous') : {
                    try {
                        Index = Index > 0 ? --Index : Embeds.length - 1

                        Embeds[Index].setFooter({
                            text : `Page ${Index + 1}/${Embeds.length}`,
                            iconURL : this.Icon ? Icon : null
                        })

                        await iMessage.edit({
                            embeds : [Embeds[Index]],
                            components : [ActionRow]
                        })
                    } catch (Error) {
                        console.error(Error)
                    }

                    break
                }

                case ('Next') : {
                    try {
                        Index = Index + 1 < Embeds.length ? ++Index : 0
                        
                        Embeds[Index].setFooter({
                            text : `Page ${Index + 1}/${Embeds.length}`,
                            iconURL : this.Icon ? Icon : null
                        })

                        await iMessage.edit({
                            embeds : [Embeds[Index]],
                            components : [ActionRow]
                        })
                    } catch (Error) {
                        console.error(Error)
                    }
                }

                case ('Input') : {
                    try {    
                    } catch (Error) {
                        console.error(Error)
                    }
                }
            }
        })
    }
}

class Pagination {
    async run (Client, Message, Embeds, Footer, Type) {
        Embeds[0].setFooter({
            text : `Page 1 out of ${Embeds.length} ${Footer ? Footer.text : ''}`,
            iconURL : Footer ? Footer.iconURL ? Footer.iconURL : null : null
        })

        var ActionRow

        Type === 'StealEmote' ? ActionRow = new ActionRowBuilder().addComponents(
            new ButtonBuilder({
                label : 'Previous',
                customId : 'PREVIOUS'
            }).setStyle('Secondary'),
            new ButtonBuilder({
                label : 'Next',
                customId : 'NEXT'
            }).setStyle('Secondary'),
            new ButtonBuilder({
                label : 'Custom Index',
                customId : 'CUSTOMINDEX'
            }).setStyle('Primary'),
            new ButtonBuilder({
                label : 'Add Emote to Server',
                customId : 'ADDEMOTE'
            }).setStyle('Success')
        ) : ActionRow = new ActionRowBuilder().addComponents(
            new ButtonBuilder({
                label : 'Previous',
                customId : 'PREVIOUS'
            }).setStyle('Primary'),
            new ButtonBuilder({
                label : 'Next',
                customId : 'NEXT'
            }).setStyle('Primary'),
            new ButtonBuilder({
                label : 'Custom Index',
                customId : 'CUSTOMINDEX'
            }).setStyle('Secondary')
        )

        var Index = 0

        const InteractionMessage = await Message.channel.send({
            embeds : [Embeds[0]],
            components : [ActionRow]
        })

        const InteractionFilter = async (Interaction) => {
            await Interaction.deferUpdate()

            if (Interaction.user.id !== Message.author.id) {
                await Interaction.followUp({
                    embeds : [
                        new EmbedBuilder({
                            description : '',
                            color : Client.color
                        })
                    ],
                    ephemeral : true
                })
            }

            return Interaction.user.id === Message.author.id
        }

        const InteractionCollector = await InteractionMessage.createMessageComponentCollector({
            InteractionFilter, time : 90000
        })

        InteractionCollector.on('collect', async (Interaction) => {
            await Interaction.deferUpdate()

            if (Interaction.user.id !== Message.author.id) return

            switch (Interaction.customId) {
                case 'PREVIOUS' :
                    Index = Index > 0 ? --Index : Embeds.length - 1

                    Embeds[Index].setFooter({
                        text : `Page ${Index + 1} out of ${Embeds.length} ${Footer ? Footer.text : ''}`,
                        iconURL : Footer ? Footer.iconURL ? Footer.iconURL : null : null
                    })

                    await InteractionMessage.edit({
                        embeds : [Embeds[Index]],
                        components : [ActionRow]
                    })
                break

                case 'NEXT' :
                    Index = Index + 1 < Embeds.length ? ++Index : 0
                    
                    Embeds[Index].setFooter({
                        text : `Page ${Index + 1} out of ${Embeds.length} ${Footer ? Footer.text : ''}`,
                        iconURL : Footer ? Footer.iconURL ? Footer.iconURL : null : null
                    })

                    await InteractionMessage.edit({
                        embeds : [Embeds[Index]],
                        components : [ActionRow]
                    })
                break

                case 'CUSTOMINDEX' :
                    for (const Component of ActionRow.components.values()) {
                        if (Component.data.custom_id === 'CUSTOMINDEX') {
                            Component.setStyle('Danger')
                        } else {
                            Component.setDisabled(true)
                        }
                    }

                    InteractionMessage.edit({
                        components : [ActionRow],
                        embeds : []
                    })

                    await Interaction.followUp({
                        embeds : [
                            new EmbedBuilder({
                                description : `**Custom Index**: Where would you like to jump? Select **1** through **${Embeds.length}** pages.`,
                            }).setColor(Client.color)
                        ],
                        ephemeral : true
                    })

                    const InputFilter = (Input) => {
                        return Input.author.id === Message.author.id
                    }

                    const InputCollector = Interaction.channel.createMessageCollector({
                        filter : InputFilter, time : 90000
                    })

                    InputCollector.on('collect', async (Input) => {
                        InputCollector.stop()

                        if (isNaN(Input.content)) {
                            Input.delete()

                            return await Interaction.followUp({
                                embeds : [
                                    new EmbedBuilder({
                                        description : `Message passed could not be parsed into an **Integer**.`,
                                    }).setColor(Client.color)
                                ],
                                ephemeral : true
                            })
                        }
                        

                        Index = parseInt(Input.content) - 1
                        
                        Embeds[Index].setFooter({
                            text : `Page ${Index + 1} out of ${Embeds.length} ${Footer ? Footer.text : ''}`,
                            iconURL : Footer ? Footer.iconURL ? Footer.iconURL : null : null
                        })

                        Input.delete()
    
                        await InteractionMessage.edit({
                            embeds : [Embeds[Index]],
                            components : [ActionRow]
                        })
                    })

                    InputCollector.on('end', async () => {
                        for (const Component of ActionRow.components.values()) {
                            if (Component.data.custom_id === 'CUSTOMINDEX') {
                                Component.setStyle('Secondary')
                            } else {
                                Component.setDisabled(false)
                            }
                        }
                    })
                break
            }
        })

        InteractionCollector.on('end', async () => {
            await InteractionMessage.edit({
                components : []
            })
        })
    }
}