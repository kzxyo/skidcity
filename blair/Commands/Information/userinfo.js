const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class UserInfo extends Command {
    constructor (Client) {
        super (Client, 'userinfo', {
            Aliases : [ 'ui', 'whois', 'info', 'user' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const User = Arguments[0] ? Message.mentions.members.first() || Message.guild.members.cache.get(Arguments[0]) || Message.guild.members.cache.find(m => String(m.user.username).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(m.displayName).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(m.user.tag).toLowerCase().includes(String(Arguments.join(' ').toLowerCase()))) || Arguments[0] : Message.member

        try {
            const Resolved = await Client.users.fetch(Client.users.resolveId(User)).catch(() => {})
            const Member = await Message.guild.members.cache.get(Resolved.id)

            if (!Resolved) {
                return new Client.Response(
                    Message, `Couldn't find a **Member** with the username: **${Arguments.join(' ')}**.`
                )
            }

            const Fields = [], MutualServers = []

            for (const Guild of Client.guilds.cache.values()) {
                if (Guild.members.cache.has(Resolved.id)) {
                    MutualServers.push(`[${Guild.name}](https://discord.com/guilds/${Guild.id})`)
                }
            }

            var Joined = '', Boosted = ''

            if (Member) {
                Joined = `Joined: <t:${Math.floor(Member.joinedTimestamp / 1000)}:f> (<t:${Math.floor(Member.joinedTimestamp / 1000)}:R>)`

                if (Member.premiumSince !== null) {
                    Boosted = `Boosted: <t:${Math.floor(Member.premiumSinceTimestamp / 1000)}:f> (<t:${Math.floor(Member.premiumSinceTimestamp / 1000)}:R>)`
                }
            }

            Fields.push({
                name : 'Informative Dates',
                value : `Registered: <t:${Math.floor(Resolved.createdTimestamp / 1000)}:f> (<t:${Math.floor(Resolved.createdTimestamp / 1000)}:R>)\n${Joined}\n${Boosted}`,
            })

            if (Member && Member.roles.cache.size > 0) {
                Fields.push({
                    name : `Roles (${Member.roles.cache.size})`,
                    value : `${Member.roles.cache.sort((a, b) => b.position - a.position).map((Role) => Role).slice(0, 5).join(', ')}${Member.roles.cache.size >= 9 ? '...' : ''}`
                })
            }

            var Important;

            if (['926627583162994718', '671744161107410968', '944099356678717500'].includes(Resolved.id)) {
                Important = 'Blair Administrator'
            } else if (Resolved.bot === true) {
                Important = 'Discord Bot'
            } else if  (Resolved.id === Message.guild.ownerId) {
                Important = 'Server Owner'
            } else if (User.guild && User.permissions.has('Administrator')) {
                Important = 'Server Administrator'
            } else {
                Important = 'N/A'
            }

            const JoinPosition = await Message.guild.members.fetch().then(Members => Members.sort((a, b) => a.joinedAt - b.joinedAt).map((User) => User.id).indexOf(Resolved.id) + 1)

            const Embed = new EmbedBuilder({
                author : {
                    name : `${Resolved.tag} (${Resolved.id})`,
                    iconURL : Resolved.displayAvatarURL({
                        dynamic : true
                    })
                },
                fields : Fields,
                thumbnail : {
                    url : Resolved.displayAvatarURL({
                        dynamic : true
                    })
                },
                footer : {
                    text : `${Important} — ${Member ? `Join Position: ${JoinPosition}, ` : ''}Mutual Servers: ${MutualServers.length}`
                }
            }).setColor(Client.Color)

            Message.channel.send({
                embeds : [
                    Embed
                ]
            })
        } catch (Error) {
            return console.error(Error)
        }
    }
}