const convert = async (content, parameters = {}) => {
    try {
        const { guild, user, member, channel, role } = parameters

        if (guild) {
            content = content
            .replaceAll('{guild}', guild.name)
            .replaceAll('{guild.name}', guild.name)
            .replaceAll('{guild.id}', guild.id)
            .replaceAll('{guild.created_at}', guild.createdAt)
            .replaceAll('{unix(guild.created_at)}', Math.floor(guild.createdTimestamp / 1000))
        }

        if (user) {
            content = content
            .replaceAll('{user}', user.tag)
            .replaceAll('{user.id}', user.id)
            .replaceAll('{user.mention}', user)
            .replaceAll('{user.name}', user.username)
            .replaceAll('{user.tag}', user.discriminator)
            .replaceAll('{user.created_at}', user.createdAt)
            .replaceAll('{unix(user.created_at)}', Math.floor(user.createdTimestamp / 1000))
            .replaceAll('{user.avatar}', user.displayAvatarURL({ size : 1024 }))
            .replaceAll('{user.bot}', user.bot ? 'Yes' : 'No')
        }

        if (member) {
            const roles = member.roles.cache.filter((role) => role.id !== guild.roles.everyone.id)

            content = content
            .replaceAll('{user.display_name}', member.displayName)
            .replaceAll('{user.nickname}', member.nickname)
            .replaceAll('{user.color}', member.displayHexColor)
            .replaceAll('{user.joined_at}', member.joinedAt)
            .replaceaLL('{unix(user.joined_at)}', Math.floor(member.joinedTimestamp / 1000))
            .replaceAll('{user.boost}', member.premiumSince !== null ? 'Yes' : 'No')
            .replaceAll('{user.boost_since}', member.premiumSince)
            .replaceAll('{unix(user.boost_since)}', Math.floor(member.premiumSinceTimestamp / 1000))
            .replaceAll('{user.display_avatar}', member.displayAvatarURL({ size : 1024 }))
            .replaceAll('{user.roles}', roles.size)
            .replaceAll('{list(user.roles)}', roles.size > 0 ? roles.sort((a, b) => b.position - a.position).map((role) => role.name).join(', ') : 'N/A') 
            .replaceAll('{user.join_position}', )
        }

        return content
    } catch (error) {
        console.error('Variables', error)

        return content
    }
}

module.exports = class Variables {
    async convert (content, options = {}) {
        if (options.member) {
            const member = options.member, joinPosition = await this.getJoinPosition(options), roles = member.roles.cache.filter(role => role.id !== options.guild.roles.everyone.id)

            content = content
            .replaceAll('{user.display_avatar}', member.displayAvatarURL({
                dynamic : true,
                size : 1024
            }))
            .replaceAll('{user.joined_at}', member.joinedAt)
            .replaceAll('{unix(user.joined_at)}', Math.floor(member.joinedTimestamp / 1000))
            .replaceAll('{user.join_position}', joinPosition.regular)
            .replaceAll('{suffix(user.join_position)}', joinPosition.ordinal)
            .replaceAll('{user.highest_role}', member.roles.highest)
            .replaceAll('{user.role_list}', roles.size > 0 ? roles.sort((a, b) => b.position - a.position).map((role) => role.name).join(', ') : 'None')
            .replaceAll('{user.role_count}', roles.size)
            .replaceAll('{user.boost}', member.premiumSince !== null ? 'Yes' : 'No')
            .replaceAll('{user.boost_since}', member.premiumSince)
            .replaceAll('{unix(user.boost_since)}', Math.floor(member.premiumSinceTimestamp / 1000))
            .replaceAll('{user.color}', member.displayHexColor)
            .replaceAll('{user.nickname}', member.nickname)
            .replaceAll('{user.display_name}', member.displayName)
        }
        if (options.message) {
            if (options.message.attachments.first()) {
                let index = 0

                options.message.attachments.map((attachment) => attachment).forEach((attachment) => {
                    content = content
                    .replaceAll(`{attachments[${index++}]}`, attachment.url)
                })
            }
        }

        
        if (options.user) {
            const user = options.user

            content = content
            .replaceAll('{user}', user.tag)
            .replaceAll('{user.id}', user.id)
            .replaceAll('{user.mention}', user)
            .replaceAll('{user.name}', user.username)
            .replaceAll('{user.tag}', user.discriminator)
            .replaceAll('{user.avatar}', user.displayAvatarURL({
                dynamic : true, 
                size : 1024
            }))
            .replaceAll('{user.bot}', user.bot ? 'Yes' : 'No')
            .replaceAll('{user.created_at}', user.createdAt)
            .replaceAll('{unix(user.created_at)}', Math.floor(user.createdTimestamp / 1000))
        }

        if (options.guild) {
            const guild = options.guild

            content = content
            .replaceAll('{guild}', guild.name)
            .replaceAll('{guild.name}', guild.name)
            .replaceAll('{guild.id}', guild.id)
            .replaceAll('{guild.owner_id}', guild.ownerId)
            .replaceAll('{guild.icon}', guild.icon ? `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.${guild.icon.startsWith('a_') ? 'gif' : 'png'}?size=1024` : 'None')
            .replaceAll('{guild.banner}', guild.banner ? `https://cdn.discordapp.com/banners/${guild.id}/${guild.banner}.${guild.banner.startsWith('a_') ? 'gif' : 'png'}?size=1024` : 'None')
            .replaceAll('{guild.splash}', guild.splash ? `https://cdn.discordapp.com/splashes/${guild.id}/${guild.splash}.${guild.splash.startsWith('a_') ? 'gif' : 'png'}?size=1024` : 'None')
            .replaceAll('{guild.created_at}', guild.createdAt)
            .replaceAll('{unix(guild.created_at)}', Math.floor(guild.createdTimestamp / 1000))
            .replaceAll('{guild.count}', guild.memberCount)
            .replaceAll('{guild.member_count}', guild.memberCount)
            .replaceAll('{guild.boost_count}', '')
            .replaceAll('{guild.boost_tier}', '')
            .replaceAll('{guild.emoji_count}', '')
            .replaceAll('{guild.role_count}', '')
            .replaceAll('{guild.channel_count}', '')
            .replaceAll('{guild.text_channel_count}', '')
            .replaceAll('{guild.voice_channel_count}', '')
            .replaceAll('{guild.category_channel_count}', '')
            .replaceAll('{guild.features}', '')
        }

        if (options.member) {
            const member = options.member, joinPosition = await this.getJoinPosition(options), roles = member.roles.cache.filter(role => role.id !== options.guild.roles.everyone.id)

            content = content
            .replaceAll('{user.display_avatar}', member.displayAvatarURL({
                dynamic : true,
                size : 1024
            }))
            .replaceAll('{user.joined_at}', member.joinedAt)
            .replaceAll('{unix(user.joined_at)}', Math.floor(member.joinedTimestamp / 1000))
            .replaceAll('{user.join_position}', joinPosition.regular)
            .replaceAll('{suffix(user.join_position)}', joinPosition.ordinal)
            .replaceAll('{user.highest_role}', member.roles.highest)
            .replaceAll('{user.role_list}', roles.size > 0 ? roles.sort((a, b) => b.position - a.position).map((role) => role.name).join(', ') : 'None')
            .replaceAll('{user.role_count}', roles.size)
            .replaceAll('{user.boost}', member.premiumSince !== null ? 'Yes' : 'No')
            .replaceAll('{user.boost_since}', member.premiumSince)
            .replaceAll('{unix(user.boost_since)}', Math.floor(member.premiumSinceTimestamp / 1000))
            .replaceAll('{user.color}', member.displayHexColor)
            .replaceAll('{user.nickname}', member.nickname)
            .replaceAll('{user.display_name}', member.displayName)
        }

        if (options.guild) {
            const guild = options.guild

            content = content
            .replaceAll('{guild}', guild.name)
            .replaceAll('{guild.name}', guild.name)
            .replaceAll('{guild.id}', guild.id)
            .replaceAll('{guild.owner_id}', guild.ownerId)
            .replaceAll('{guild.icon}', guild.icon ? `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.${guild.icon.startsWith('a_') ? 'gif' : 'png'}?size=1024` : 'None')
            .replaceAll('{guild.banner}', guild.banner ? `https://cdn.discordapp.com/banners/${guild.id}/${guild.banner}.${guild.banner.startsWith('a_') ? 'gif' : 'png'}?size=1024` : 'None')
            .replaceAll('{guild.splash}', guild.splash ? `https://cdn.discordapp.com/splashes/${guild.id}/${guild.splash}.${guild.splash.startsWith('a_') ? 'gif' : 'png'}?size=1024` : 'None')
            .replaceAll('{guild.created_at}', guild.createdAt)
            .replaceAll('{unix(guild.created_at)}', Math.floor(guild.createdTimestamp / 1000))
            .replaceAll('{guild.count}', guild.memberCount)
            .replaceAll('{guild.member_count}', guild.memberCount)
            .replaceAll('{guild.boost_count}', '')
            .replaceAll('{guild.boost_tier}', '')
            .replaceAll('{guild.emoji_count}', '')
            .replaceAll('{guild.role_count}', '')
            .replaceAll('{guild.channel_count}', '')
            .replaceAll('{guild.text_channel_count}', '')
            .replaceAll('{guild.voice_channel_count}', '')
            .replaceAll('{guild.category_channel_count}', '')
            .replaceAll('{guild.features}', '')
        }

        if (options.channel) {
            const channel = options.channel

            content = content
            .replaceAll('{channel}', channel.name)
            .replaceAll('{channel.name}', channel.name)
            .replaceAll('{channel.id}', channel.id)
            .replaceAll('{channel.mention}', channel)
            .replaceAll('{channel.topic}', channel.topic || 'None')
        }

        return content
    }

    async getJoinPosition (options) {
        const members = await options.guild.members.fetch()

        const joinPosition = await members.sort((a, b) => a.joinedAt - b.joinedAt).map((user) => user.id).indexOf(options.member.id) + 1

        const ordinaljoinPosition = (joinPosition.toString().endsWith(1) && !joinPosition.toString().endsWith(11)) ? 'st' : (joinPosition.toString().endsWith(2) && !joinPosition.toString().endsWith(12)) ? 'nd' : (joinPosition.toString().endsWith(3) && !joinPosition.toString().endsWith(13)) ? 'rd' : 'th'

        return {
            regular : joinPosition,
            ordinal : joinPosition + ordinaljoinPosition
        }
    }
}

const data = {
    test: {
        name: 'nick'
    }
}

const content = 'Hi {test.name}'

const parse = (match, variable) => {
    let value = data

    try {
        for (const prop of variable.split('.')) {
            value = value[prop]
        }

        return String(value)
    } catch (error) {
        return match
    }
}

return content.replace(/{([a-zA-Z_.]+)}/g, (match, variable) => parse(match, variable))