const { MessageEmbed } = require('discord.js');

function get_member_or_self(message, choice) {
    let member
    if (!choice) {
        member = message.member
    } else {
        member = choice.match(/^<@!?(\d+)>$/);
        if (member) {
            member = member[1]
            return message.guild.members.cache.get(member)
        } else {
            member =
                message.guild.members.cache.find(u => u.id === choice) ||
                message.guild.members.cache.find(u => u.user.username.toLowerCase() === choice.toLowerCase()) ||
                message.guild.members.cache.find(u => u.user.username.toLowerCase().startsWith(choice.toLowerCase())) ||
                message.guild.members.cache.find(u => u.displayName.toLowerCase() === choice.toLowerCase()) ||
                message.guild.members.cache.find(u => u.displayName.toLowerCase().startsWith(choice.toLowerCase())) ||
                message.guild.members.cache.find(u => u.user.tag.toLowerCase() === choice.toLowerCase()) ||
                message.client.users.cache.find(u => u.username + '#' + u.discriminator === choice)
        }
    }
    if (!member) return
    if (member) member = member.id
    const found = message.guild.members.cache.get(member)
    return found
}

function get_member(message, choice) {
    let member
    if (!choice) {
        return
    } else {
        member = choice.match(/^<@!?(\d+)>$/);
        if (member) {
            member = member[1]
            return message.guild.members.cache.get(member)
        } else {
            member =
                message.guild.members.cache.find(u => u.id === choice) ||
                message.guild.members.cache.find(u => u.user.username.toLowerCase() === choice.toLowerCase()) ||
                message.guild.members.cache.find(u => u.user.username.toLowerCase().startsWith(choice.toLowerCase())) ||
                message.guild.members.cache.find(u => u.displayName.toLowerCase() === choice.toLowerCase()) ||
                message.guild.members.cache.find(u => u.displayName.toLowerCase().startsWith(choice.toLowerCase())) ||
                message.guild.members.cache.find(u => u.user.tag.toLowerCase() === choice.toLowerCase()) ||
                message.client.users.cache.find(u => u.username + '#' + u.discriminator === choice)
        }
    }
    if (!member) return
    if (member) member = member.id
    const found = message.guild.members.cache.get(member)
    return found
}

function join_position(message, user) {
    let result = message.guild.members.cache
        .sorted((a, b) => a.joinedAt - b.joinedAt)
        .findIndex(m => m.id === user) + 1
    return result
}

function mutual_guilds(message, user) {
    let result = message.client.guilds.cache.filter(guild => !!guild.members.cache.get(user))
    let mutuals = result.size
    return mutuals
}

function get_channel(message, channel) {
    let get = channel.match(/^<#(\d+)>$/)
    if (get) {
        get = get[1]
        return message.guild.channels.cache.get(get)
    } else {
        get =
            message.guild.channels.cache.filter(c => c.type === 'text').get(channel) ||
            message.guild.channels.cache.filter(c => c.type === 'text').find(c => c.name.toLowerCase() === channel.toLowerCase()) ||
            message.guild.channels.cache.filter(c => c.type === 'text').find(c => c.name.toLowerCase().includes(channel.toLowerCase())) ||
            message.channel
        if (!get) return
        if (get) get = get.id
        return message.guild.channels.cache.get(get)
    }
}


function get_role(message, choice) {
    let role
    if (!choice) {
        return
    } else {
        role =
            message.mentions.roles.first() ||
            message.guild.roles.cache.find(r => r.id === choice) ||
            message.guild.roles.cache.find(r => r.name.toLowerCase() === choice.toLowerCase()) ||
            message.guild.roles.cache.find(r => r.name.toLowerCase().includes(choice.toLowerCase()))
    }
    if (!role) return
    const found = message.guild.roles.cache.get(role.id)
    return found
}

function paramater(param, args) {
    let choice
    if (!args.includes(`$${param}`)) {
        choice = args.split()
    } else {
        choice = args.split(`$${param}`)
    }
    return choice
}

function handle_link(link) {
    if (!link) return false
    if (link.startsWith('http://cdn.discordapp.com/')) {
        return true
    } else if (link.startsWith('https://cdn.discordapp.com/')) {
        return true
    } else {
        return false
    }
}


module.exports = {
    get_member_or_self,
    get_member,
    join_position,
    mutual_guilds,
    get_channel,
    get_role,
    paramater,
    handle_link
}