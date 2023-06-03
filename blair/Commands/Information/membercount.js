const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

const ms = require('ms'), time = ms('24h')

module.exports = class MemberCount extends Command {
    constructor (Client) {
        super (Client, 'membercount', {
            Aliases : [ 'mc', 'memberscount' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        try {
            Message.channel.send({
                embeds : [
                    new EmbedBuilder({
                        fields: [
                            {
                                name: 'Members',
                                value: `${Message.guild.memberCount}`,
                                inline: true
                            },
                            {
                                name: 'Humans',
                                value: `${Message.guild.members.cache.filter(m => !m.user.bot).size}`,
                                inline: true
                            },
                            {
                                name: 'Bots',
                                value: `${Message.guild.members.cache.filter(m => m.user.bot).size}`,
                                inline: true
                            }
                        ],
                        footer: {
                            text: `${Message.guild.members.cache.filter(Member => Member.presence && Member.presence.status !== 'offline').size} Members Online, +${Message.guild.members.cache.filter(m => Date.now() - new Date(m.joinedAt).getTime() < time).size} Members`
                        }
                    }).setColor(Client.Color)
                ]
            })
        } catch (Error) {
            return new Client.Error(
                Message, 'membercount', Error
            )
        }
    }
}