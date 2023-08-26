const proper = (str) => `${str}`.trim()
const error = (str) => `I wasn't able to find that **${str}**`

const Discord = require('discord.js')
const { parse } = require('twemoji-parser')
const chroma = require('chroma-js')
const coloras = require('coloras')
const ColorThief = require('color-thief-node')
const rgb2hex = require('rgb2hex')

const regexes = {
    member : /^<@!?(\d+)>$/,
    channel : /^<#(\d+)>$/
}

class Converters {
    constructor (bot) {
        this.bot = bot
    }

    // Bot
    async guild () {}
    async invite () {}
    async user () {}
    async command () {}

    // Guild

    async member (message, text, options = {}) {
        try {
            text = proper(text)

            let member

            const match = text.match(regexes.member)

            if (match) {
                member = match[1]
            } else {
                if (message.guild.memberCount !== message.guild.members.cache.size) { await message.guild.members.fetch() }

                member = message.guild.members.cache.get(text) || message.guild.members.cache.find((member) => member.user.username.toLowerCase().includes(text.toLowerCase()) || member.user.tag.toLowerCase().includes(text.toLowerCase()) || member.displayName.toLowerCase().includes(text.toLowerCase()))
            }

            if (!member) {
                if (options.response !== false) {
                    this.bot.warn(
                        message, error('member')
                    )
                }

                return false
            }

            return await message.guild.members.fetch(member)
        } catch (error) {
            console.error('Member', error)

            return false
        }
    }

    async channel (message, text, options = {}) {
        try {
            text = proper(text)

            let channel

            const match = text.match(regexes.channel)

            if (match) {
                channel = message.guild.channels.cache.get(match[1])
            } else {
                channel = message.guild.channels.cache.get(text) || message.guild.channels.cache.find((channel) => channel.name.toLowerCase().includes(text.toLowerCase()))
            }

            if (!channel || options.type && channel.type !== options.type) {
                if (options.response !== false) {
                    this.bot.warn(
                        message, error('channel')
                    )
                }

                return false
            }

            return channel
        } catch (error) {
            console.error('Channel', error)

            return false
        }
    }

    async role () {}
    async emoji () {}
    async sticker () {}

    // Miscellaneous
    async message () {}
    async attachment () {}
    async color () {}
    async date () {}
}


module.exports = class Convefrters {
    constructor (bot) {
        this.bot = bot
    }

    async member (message, str, parameters = {}) {
        str = proper(str)

        let member, fail = `I wasn't able to find that **member**`

        const memberRegex = /^<@!?(\d+)>$/, memberMatch = str.match(memberRegex)

        if (memberMatch) {
            member = memberMatch[1]
        } else {
            if (message.guild.memberCount !== message.guild.members.cache.size) {
                await message.guild.members.fetch()
            }

            member = message.guild.members.cache.get(str) || message.guild.members.cache.find((member) => String(member.user.username).toLowerCase().includes(String(str).toLowerCase()) || String(member.user.tag).toLowerCase().includes(String(str).toLowerCase()) || String(member.displayName).toLowerCase().includes(String(str).toLowerCase()))
        }

        if (!member) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }

            return false
        }

        return await message.guild.members.fetch(member)
    }

    role (message, str, parameters = {}) {
        str = proper(str)

        let role, fail = `I wasn't able to find that **role**`

        const roleRegex = /^<@&(\d+)>$/, roleMatch = str.match(roleRegex)

        if (roleMatch) {
            role = message.guild.roles.cache.get(roleMatch[1])
        } else {
            role = message.guild.roles.cache.get(str) || message.guild.roles.cache.find((role) => role.name.toLowerCase().includes(str.toLowerCase()))
        }

        if (!role) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }

            return false
        }

        return role
    }

    channel (message, str, parameters = {}) {
        str = proper(str)

        let channel, fail = `I wasn't able to find that **channel**`

        const channelRegex = /^<#(\d+)>$/, channelMatch = str.match(channelRegex)

        if (channelMatch) {
            channel = message.guild.channels.cache.get(channelMatch[1])
        } else {
            channel = message.guild.channels.cache.get(str) || message.guild.channels.cache.find((channel) => channel.name.toLowerCase().includes(str.toLowerCase()))
        }

        if (!channel || parameters.type && channel.type !== parameters.type) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }
            
            return false
        }

        return channel
    }
    
    async command (message, str, parameters = {}) {
        str = proper(str)

        const args = str.split(' '), fail = `Command \`${str}\` doesn't exist`

        let command = this.bot.resolveCommand(args[0].toLowerCase()), latest = command

        if (!command) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }

            return false 
        }

        for (let i = 1; i < args.length; i++) {
            const subCommand = this.bot.resolveSubCommand(`${command.name} ${args[i]}`)

            if (!subCommand) {
                if (parameters.latest) {
                    return latest
                } else {
                    if (parameters.response) {
                        this.bot.warn(
                            message, fail
                        )
                    }

                    return false
                }
            }

            command = subCommand, latest = subCommand
        }

        if (command.guarded && !parameters.guarded) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }

            return false
        }

        return parameters.latest ? latest : command
    }

    async message (message, str, parameters = {}) {
        const match = str.match(/^https?:\/\/(?:(?:www|canary)\.)?discord(?:app)?\.com\/channels\/(\d{17,19})\/(\d{17,19})\/(\d{17,19})$/)

        const fail = `Message "${str}" not found.`

        if (!match) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }

            return false
        }

        const [, guildID, channelID, messageID] = match

        const channel = message.guild.channels.cache.get(channelID)

        if (!channel) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }

            return false
        }

        const fetched = await channel.messages.fetch(messageID).catch(() => {})

        if (!fetched) {
            if (parameters.response) {
                this.bot.warn(
                    message, fail
                )
            }

            return false
        }

        return fetched
    }

    async attachment (message, str, parameters = {}) {
        try {
            const { extentions = [ 'png', 'jpg', 'jpeg', 'gif' ], types = [], finder } = parameters

            const urlRegex = new RegExp('\\.(' + extentions.map((extention) => `\\b${extention}\\b`).join('|') + ')(\\?.*)?$', 'i'), attachmentRegex = /^https?:\/\/((cdn|media)\.discordapp\.(com|net)|blair\.win)\/.+/i

            let name, url, isArgs

            const attachment = message.attachments?.first(), sticker = message.stickers?.first(), reference = message.reference

            switch (true) {
                case (attachment !== undefined && types.includes('attachment')) : {
                    name = attachment.name, url = attachment.url, isArgs = false
                    break
                }

                case (sticker !== undefined && types.includes('sticker')) : {
                    name = sticker.name, url = sticker.url, isArgs = false
                    break
                }

                case (reference !== null && types.includes('reference')) : {
                    const ref = await message.channel.messages.fetch(reference.messageId).catch(() => {})

                    if (ref) {
                        const refAttachment = ref.attachments?.first(), refSticker = ref.stickers?.first()

                        switch (true) {
                            case (refAttachment !== undefined && types.includes('attachment')) : {
                                name = refAttachment.name, url = refAttachment.url, isArgs = false
                                break
                            }

                            case (refSticker !== undefined && types.includes('sticker')) : {
                                name = refSticker.name, url = refSticker.url, isArgs = false
                                break
                            }

                            default : {
                                return false
                            }
                        }
                    } else {
                        return false
                    }
                    
                    break
                }

                case (str.length === 0 && finder) : {
                    const messages = await message.channel.messages.fetch({ limit : 100 })

                    const filter = messages.filter((message) => {
                        const msgAttachment = message.attachments?.first(), msgSticker = message.stickers?.first()

                        switch (true) {
                            case (msgAttachment !== undefined && types.includes('attachment')) : {
                                return true
                            }

                            case (msgSticker !== undefined && types.includes('sticker')) : {
                                return true
                            }

                            default : {
                                return false
                            }
                        }
                    })

                    if (filter.size > 0) {
                        const message = filter.first(), attachment = message.attachments?.first(), sticker = message.stickers?.first()

                        if (attachment) {
                            name = attachment.name, url = attachment.url, isArgs = false
                        } else if (sticker && types.includes('sticker')) {
                            name = sticker.name, url = sticker.url, isArgs = false
                        }
                    } else {
                        return false
                    }

                    break
                }

                case (str.length !== 0) : {
                    url = str.trim(), name = name = null, isArgs = true

                    if (!urlRegex.test(url) || !attachmentRegex.test(url)) {
                        const link = await this.message(message, str), member = await this.member(message, str), emoji = this.emoji(str, {
                            ignoreCache : true
                        })

                        if (link && types.includes('message')) {
                            const linkAttachment = link.attachments?.first(), linkSticker = link.stickers?.first()

                            switch (true) {
                                case (linkAttachment !== undefined && types.includes('attachment')) : {
                                    name = linkAttachment.name, url = linkAttachment.url, isArgs = true
                                    break
                                }

                                case (linkSticker !== undefined && types.includes('sticker')) : {
                                    name = linkSticker.name, url = linkSticker.url, isArgs = true
                                    break
                                }

                                default : {
                                    return false
                                }
                            }
                        } else if (member && types.includes('member')) {
                            name = this.bot.util.random(null, 6), url = member.displayAvatarURL({
                                size : 1024
                            }).replace('webp', 'png'), isArgs = true
                        } else if (emoji && (types.includes('emoji') || types.includes('emote'))) {
                            if (emoji.type === 'emoji' && types.includes('emoji')) {
                                name = this.bot.util.random(null, 6), url = emoji.url, isArgs = true
                            } else if (emoji.type === 'emote' && types.includes('emote')) {
                                name = emoji.name, url = emoji.url, isArgs = true
                            } else {
                                return false
                            }
                        } else {
                            return false
                        }
                    }
                }

                break
            }

            return {
                name : name,
                url : url,
                isArgs : isArgs
            }
        } catch (error) {
            console.error('Attachment', error)
        }
    }

    emoji (emoji, parameters = {}) {
        const emote = Discord.parseEmoji(emoji)
        
        if (emote.id) {
            const fetchedEmote = this.bot.emojis.cache.get(emote.id)
            
            if (!fetchedEmote && !parameters.ignoreCache) {
                return false
            }
            
            return {
                emoji : fetchedEmote || null,
                identifier : fetchedEmote?.id || null,
                type : 'emote',
                url : `https://cdn.discordapp.com/emojis/${emote.id}${emote.animated ? '.gif' : '.png'}?size=1024`,
                name : emote.name
            }
        }
        
        const parsedEmoji = parse(
            emoji, {
                assetType : 'png'
            }
        )
        
        if (parsedEmoji.length === 1 && parsedEmoji[0].type === 'emoji') {
            return {
                emoji : parsedEmoji[0].text,
                identifier : parsedEmoji[0].text,
                type : 'emoji',
                url : parsedEmoji[0].url,
                name : parsedEmoji[0].text
            }
        }

        return false
    }

    async color (str, options = {}) {
        let colorHex

        if (options.dominant) {
            const Rgb = await ColorThief.getColorFromURL(options.dominant.replace('webp', 'png'))

            colorHex = rgb2hex(`rgb(${Rgb})`).hex
        } else if (options.random) {
            colorHex = new coloras.Color(null).toHex()
        } else {
            try {
                const colorObject = chroma(str)
                colorHex = colorObject.hex()
    
                if (!/^#([0-9A-F]{3}){1,2}$/i.test(colorHex)) {
                    throw new Error('Invalid')
                }
            } catch (error) {
                str = str.replace('#', '')
            
                const hex = parseInt(str, 16).toString(16)
                const paddedHex = hex.padStart(6, '0')
                const outputHex = '#' + paddedHex
                
                colorHex = outputHex
            }
        }

        if (!/^#([0-9A-F]{3}){1,2}$/i.test(colorHex)) {
            return false
        }

        return colorHex.replaceAll('#000000', '#000001')
    }
}