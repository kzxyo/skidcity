const Discord = require('discord.js');

module.exports = class MessageParser {
    constructor (bot, code) {
        let message = '', embeds = [], buttons = [], attachments = [], stickers = []

        const setRegex = /\{set:(.*?)\}/gis, setMatches = code.match(setRegex)

        for (const match of setMatches || []) {
            const propertiesString = match.replace(/\{set:|\}/g, '')

            const properties = this.splitProperties(propertiesString, [
                '$name:',
                '$value:'
            ])

            let setName, setValue

            for (const property of properties) {
                const colenIndex = property.indexOf(':')
                
                if (colenIndex === -1) continue

                const key = property.substring(0, colenIndex).trim()
                const value = property.substring(colenIndex + 1).trim()

                switch (key) {
                    case ('$name') : {
                        setName = value

                        break
                    }

                    case ('$value') : {
                        setValue = value

                        break
                    }
                }
            }

            if (setName && setValue) {
                code = code.replaceAll(`{${setName}}`, setValue)
            }
        }

        const embedRegex = /\{embed:(.*?)\}/gis, embedMatches = code.match(embedRegex)

        for (const match of embedMatches || []) {
            const propertiesString = match.replace(/\{embed:|\}/g, '')
            
            const properties = this.splitProperties(propertiesString, [
                '$color:',
                '$author:',
                '$title:',
                '$url:',
                '$description:',
                '$field:',
                '$footer:',
                '$thumbnail:',
                '$image:',
                '$timestamp'
            ])

            let embed = { fields : [] }, color = '#2b2d31'

            for (const property of properties) {
                let key, value

                if (property.trim() === '$timestamp') {
                    key = '$timestamp'
                    value = new Date()
                } else {
                    const colenIndex = property.indexOf(':')

                    if (colenIndex === -1) continue

                    key = property.substring(0, colenIndex).trim()
                    value = property.substring(colenIndex + 1).trim()
                }

                switch (key) {
                    case ('$color') : {
                        if (String(value).toLowerCase() === 'invisible') {
                            color = '#2b2d31'
                        } else {
                            color = value
                        }

                        break
                    }

                    case ('$author') : {
                        const author = value.split('&&')

                        embed.author = {
                            name : author[0]?.trim() || null,
                            url : author[2]?.trim() || null
                        }

                        const regex = /^https:\/\/(cdn\.discordapp\.com|media\.discordapp\.net|lastfm\.freetls\.fastly\.net)/i, iconURL = author[1]?.trim() || null

                        if (iconURL && regex.test(iconURL)) {
                            embed.author.iconURL = iconURL
                        }

                        break
                    }

                    case ('$title') : {
                        embed.title = value?.slice(0, 256).trim() || null

                        break
                    }

                    case ('$url') : {
                        embed.url = value?.trim() || null

                        break
                    }

                    case ('$description') : {
                        embed.description = value?.slice(0, 4096).trim() || null

                        break
                    }

                    case ('$field') : {
                        const field = value.split('&&')

                        if (value) {
                            embed.fields.push({
                                name : field[0]?.trim() || null,
                                value : field[1]?.trim().replace('inline', '') || null,
                                inline : field[1]?.trim().includes('inline') ? true : false
                            })
                        }

                        break
                    }

                    case ('$footer') : {
                        const footer = value.split('&&')

                        embed.footer = {
                            text : footer[0]?.trim() || null
                        }

                        const regex = /^https:\/\/(cdn\.discordapp\.com|media\.discordapp\.net|lastfm\.freetls\.fastly\.net)/i, iconURL = footer[1]?.trim() || null

                        if (iconURL && regex.test(iconURL)) {
                            embed.footer.iconURL = iconURL
                        }

                        break
                    }

                    case ('$thumbnail') : {
                        const regex = /^https:\/\/(cdn\.discordapp\.com|media\.discordapp\.net|lastfm\.freetls\.fastly\.net)/i, iconURL = value?.trim() || null

                        if (value && regex.test(iconURL)) {
                            embed.thumbnail = {
                                url : iconURL
                            }
                        }

                        break
                    }

                    case ('$image') : {
                        const regex = /^https:\/\/(cdn\.discordapp\.com|media\.discordapp\.net|lastfm\.freetls\.fastly\.net)/i, iconURL = value?.trim() || null

                        if (value && regex.test(iconURL)) {
                            embed.image = {
                                url : iconURL
                            }
                        }

                        break
                    }

                    case ('$timestamp') : {
                        embed.timestamp = value

                        break
                    }
                }
            }

            if (embed.author || embed.title || embed.url || embed.description || embed.fields?.length > 0 || embed.footer || embed.image || embed.thumbnail) {
                embeds.push(new Discord.EmbedBuilder(embed).setColor(color))
            }
        }

        const buttonRegex = /\{button:(.*?)\}/gis, buttonMatches = code.match(buttonRegex)

        for (const match of buttonMatches || []) {
            const propertiesString = match.replace(/\{button:|\}/g, '')
            
            const properties = this.splitProperties(propertiesString, [
                '$style:',
                '$label:',
                '$emoji:',
                '$url:',
                '$disabled'
            ])

            let button = {}, style = 'Primary', url = null, disabled = false

            for (const property of properties) {
                let key, value

                if (property.trim() === '$disabled') {
                    key = '$disabled'
                    value = true
                } else {
                    const colenIndex = property.indexOf(':')

                    if (colenIndex === -1) continue

                    key = property.substring(0, colenIndex).trim()
                    value = property.substring(colenIndex + 1).trim()
                }

                switch (key) {
                    case ('$style') : {
                        const buttonStyles = {
                            'primary' : 'Primary',
                            'secondary' : 'Secondary',
                            'success' : 'Success',
                            'danger' : 'Danger',
                            'link' : 'Link'
                        }
                    
                        const checkStyle = String(value).toLowerCase()
                        if (buttonStyles.hasOwnProperty(checkStyle)) {
                            style = buttonStyles[checkStyle]
                        }
                    
                        break
                    }

                    case ('$label') : {
                        button.label = value?.slice(0, 80).trim() || null

                        break
                    }

                    case ('$emoji') : {
                        button.emoji = value?.trim() || null
                        
                        break
                    }

                    case ('$url') : {
                        url = value?.trim() || null

                        break
                    }

                    case ('$disabled') : {
                        disabled = value

                        break
                    }
                }
            }

            if (url) style = 'Link'

            if (button.label || button.emoji) {
                if (style === 'Link') {
                    button.url = url
                } else {
                    button.customId = bot.util.random('abcdefghijklmnopqrstuvwxyz1234567890', 10) 
                }

                const parsedButton = new Discord.ButtonBuilder(button).setDisabled(disabled).setStyle(style)
                
                buttons.push(parsedButton)
            }
        }

        const attachmentRegex = /\{attachment:(.*?)\}/gis, attachmentMatches = code.match(attachmentRegex)

        for (const match of attachmentMatches || []) {
            const propertiesString = match.replace(/\{attachment:|\}/g, '')
            
            const properties = this.splitProperties(propertiesString, [
                '$url:',
                '$name:',
                '$description:'
            ])

            let attachment = {}, file = null

            for (const property of properties) {
                const colenIndex = property.indexOf(':')
                
                if (colenIndex === -1) continue

                const key = property.substring(0, colenIndex).trim()
                const value = property.substring(colenIndex + 1).trim()

                switch (key) {
                    case ('$url') : {
                        const regex = /^https:\/\/(cdn\.discordapp\.com|media\.discordapp\.net)/i, url = value?.trim() || null

                        if (url && regex.test(url)) {
                            file = url
                        }

                        break
                    }

                    case ('$name') : {
                        attachment.name = value?.slice(0, 256).trim() || null

                        break
                    }
                }
            }

            if (file) {
                
                const regex = /\.([A-Za-z0-9]+)$/g, match = regex.exec(file)

                attachment.name = bot.util.random('abcdefghijklmnopqrstuvwxyz1234567890', 10) + '.' + match[1]

                const parsedAttachment = new Discord.AttachmentBuilder(file, attachment)
                
                attachments.push(parsedAttachment)
            }
        }

        message = code.replace(setRegex, '').replace(embedRegex, '').replace(buttonRegex, '').replace(attachmentRegex, '').slice(0, 2000).trim()
        
        const maxButtons = 5, maxActionRows = 5, components = []

        for (let i = 0; i < buttons.length && components.length < maxActionRows; i += maxButtons) {
            const row = new Discord.ActionRowBuilder()

            const slicedButtons = buttons.slice(i, i + maxButtons)

            slicedButtons.forEach((button) => row.addComponents(button))

            components.push(row)
        }

        return {
            content : message.trim(),
            embeds : embeds?.slice(0, 10),
            components: components,
            files : attachments?.slice(0, 10)
        }
    }

    splitProperties (propertiesString, keys) {
        let result = [], startIndex = 0

        for (let i = 0; i < propertiesString.length; i++) {
            for (let j = 0; j < keys.length; j++) {
                if (propertiesString.startsWith(keys[j], i)) {
                    if (i > startIndex) {
                        result.push(propertiesString.substring(startIndex, i))
                    }

                    startIndex = i

                    break
                }
            }
        }

        if (startIndex < propertiesString.length) {
            result.push(propertiesString.substring(startIndex))
        }

        return result
    }
}
