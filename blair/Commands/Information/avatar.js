const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class Avatar extends Command {
    constructor (Client) {
        super (Client, 'avatar', {
            Aliases : ['av', 'avi', 'pfp', 'ab', 'ag']
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

            const Avatar = Resolved.displayAvatarURL({ dynamic : true, size : 1024 })

            Message.channel.send({
                embeds : [
                    new EmbedBuilder({
                        title : `${Resolved.tag}'s avatar`,
                        url : Avatar,
                        image : {
                            url : Avatar
                        }
                    }).setColor('#c6bfc6')
                ]
            })
        } catch (Error) {
            console.error(Error)
        }
    }
}