const Discord = require('discord.js')

module.exports = class Response {
    constructor (bot) {
        this.bot = bot

        this.response = this.response.bind(this)
        this.approve = this.approve.bind(this)
        this.warn = this.warn.bind(this)
        this.neutral = this.neutral.bind(this)
    }

    response (message, content, parameters = {}) {
        try {
            const embed = new Discord.EmbedBuilder({
                description : `${parameters.text ? `${content}\n<:dash:1109708012806996048>  ${parameters.text}` : `<:dash:1109708012806996048> ${content}`}`
            }).setColor(parameters.color)

            if (parameters.author) {
                embed.setAuthor(parameters.author)
            }

            if (parameters.fields) {
                embed.addFields(parameters.fields)
            }

            if (parameters.footer) {
                embed.setFooter(parameters.footer)
            }

            let sent, object = {
                embeds : [
                    embed
                ],
                components : parameters.components || []
            }

            if (parameters.object) {
                return object
            }

            if (parameters.edit) {
                sent = parameters.edit.edit(object)
            } else if (parameters.reply !== false) {
                sent = message.reply(object)
            } else {
                sent = message.channel.send(object)
            }

            return sent
        } catch (error) {
            console.error('Response', error)
        }
    }

    // Positive

    approve (message, content, parameters = {}) {
        return this.response(
            message, content, {
                ...parameters,
                emoji : this.bot.emotes.approve,
                color : this.bot.colors.approve
            }
        )
    }

    // Neutral

    neutral (message, content, parameters = {}) {
        return this.response(
            message, content, {
                color : parameters.color ? parameters.color : this.bot.colors.neutral,
                ...parameters
            }
        )
    }

    async confirm (message, content, callback, parameters = {}) {
        try {
            const msg = await this.neutral(
                message, `${content}`, {
                    components : [
                        new Discord.ActionRowBuilder({
                            components : [
                                new Discord.ButtonBuilder({
                                    label : 'Approve',
                                    customId : 'Approve'
                                }).setStyle('Success'),
                                new Discord.ButtonBuilder({
                                    label : 'Decline',
                                    customId : 'Decline'
                                }).setStyle('Danger')
                            ]
                        })
                    ],
                    ...parameters
                }
            )

            const filter = async (interaction) => {
                await interaction.deferUpdate()

                if (interaction.user.id !== message.author.id) {

                }

                return interaction.user.id === message.author.id
            }

            const collector = msg.createMessageComponentCollector({ 
                filter, time : 60000 
            })

            collector.on('collect', async (interaction) => {
                switch (interaction.customId) {
                    case ('Approve') : { 
                        collector.stop()
                        msg.delete()
                        callback()

                        break
                    }

                    case ('Decline') : {
                        collector.stop()
                        msg.delete()
                        message.delete()


                        break
                    }
                }
            })

            collector.on('end', (collected) => {
                if (collected.size === 0) {
                    msg.delete()
                    message.delete()
                }          
            })
        } catch (error) {
            console.error('Confirm', error)
        }
    }

    help (message, command) {
        try {
            message.channel.send({
                embeds : [
                    new Discord.EmbedBuilder({
                        author : {
                            name : message.member.displayName,
                            iconURL : message.member.displayAvatarURL()
                        },
                        description : `${command.description || ''}\n\`\`\`bf\nSyntax: ${message.prefix}${command.syntax ? `${command.name} ${command.syntax}` : command.name}\n${command.example ? `Example: ${message.prefix}${command.name} ${command.example}` : ''}\`\`\``
                    }).setColor(message.client.colors.neutral)
                ]
            })
        } catch (error) {
            console.error('Help', error)
        }
    }

    // Negative

    warn (message, content, parameters) {
        return this.response(
            message, content, {
                ...parameters,
                emoji : this.bot.emotes.warn,
                color : this.bot.colors.warn
            }
        )
    }

    async error (message, command, error) {
        try {
            console.error(error)

            const ID = message.client.util.random(null, 13)

            const msg = await this.warn(
                message, `An unknown error occurred while running **${command}**`, {
                    text : `Please report error \`${ID}\` in the  [**Discord Server**](https://discord.gg/blair)`
                }
            )

            message.client.db.query('INSERT INTO tracebacks (command, error, error_id, guild_id, channel_id, user_id, message_id, timestamp) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)', {
                bind : [
                    command, error.message, ID, message.guild.id, message.channel.id, message.author.id, msg.id, message.createdTimestamp
                ]
            })
        } catch (error) {
            console.error('Error', error)
        }
    }
}