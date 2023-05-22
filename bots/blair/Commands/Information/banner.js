const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

const Phin = require('phin')

module.exports = class Banner extends Command {
    constructor (Client) {
        super (Client, 'banner', {
            
        })
    }

    async Invoke (Client, Message, Arguments) {
        const User = Arguments[0] ? Message.mentions.members.first() || Message.guild.members.cache.get(Arguments[0]) || Message.guild.members.cache.find(m => String(m.user.username).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(m.displayName).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(m.user.tag).toLowerCase().includes(String(Arguments.join(' ').toLowerCase()))) || Arguments[0] : Message.member

        try {
            const Resolved = await Client.users.fetch(Client.users.resolveId(User)).catch(() => {})

            if (!Resolved) {
                return new Client.Response(
                    Message, `Couldn't find a **Member** with the username: **${Arguments.join(' ')}**.`
                )
            }

            Phin({
                url : `https://discord.com/api/v10/users/${Resolved.id}`,
                method : 'GET',
                parse : 'json',
                headers : {
                    'Authorization' : `Bot ${process.env.DiscordToken}`
                }
            }).then(async (Results) => {
                const { banner, banner_color } = Results.body

                var Banner

                if (banner) {
                    Banner = `https://cdn.discordapp.com/banners/${Resolved.id}/${banner}${banner.startsWith('a_') ? '.gif' : '.png'}?size=1024`
                } else if (banner_color) {
                    Banner = `https://singlecolorimage.com/get/${banner_color.replace('#', '')}/400x100`
                } else {
                    return new Client.Embed(
                        Message, `${Resolved === Message.author ? `You have not set a banner.` : `Member **${Resolved.tag}** has not set a banner.`}`
                    )
                }

                Message.channel.send({
                    embeds : [
                        new EmbedBuilder({
                            title : `${Resolved.tag}'s banner`,
                            url : Banner,
                            image : {
                                url : Banner
                            }
                        }).setColor('#c6bfc6')
                    ]
                })
            })
        } catch (Error) {
            return new Client.Error(
                Message, 'banner', Error
            )
        }
    }
}