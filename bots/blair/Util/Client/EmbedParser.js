const Discord = require('discord.js')

module.exports = class EmbedParser {
    constructor (Code) {
        const Content = Code.split('$v')

        var Embed = { fields : [] }, Color = null, Message = '', Buttons = []

        for (var Item of Content) {
            Item = Item.slice(Item.indexOf('{') + 1, Item.lastIndexOf('}'))

            switch (Item) {
                case (Item.startsWith('message:') ? Item : '') : {
                    Message = Item.replace('message:', '').trim()

                    break
                }

                case (Item.startsWith('author:') ? Item : '') : {
                    const Author = Item.replace('author:', '')
                    const Split = Author.split('&&')

                    if (Split[1]) {
                        const Domain = (new URL(Split[1]))

                        if (!Domain || Domain.host !== 'blair.win' && Domain.host !== 'media.discordapp.net' && Domain.host !== 'cdn.discordapp.com') {
                            Split[1] = null
                        }
                    }

                    Embed.author = {
                        name : Split[0].trim(),
                        iconURL : Split[1] ? Split[1].trim() : null,
                        url : Split[2] ? Split[2].trim() : null
                    }

                    break
                }

                case (Item.startsWith('title') ? Item : '') : {
                    Embed.title = Item.replace('title:', '').trim()

                    break
                }

                case (Item.startsWith('url') ? Item : '') : {
                    Embed.url = Item.replace('url:', '').trim() 
                    
                    console.log(Embed.url)

                    break
                }

                case (Item.startsWith('description:') ? Item : '') : {
                    Embed.description = Item.replace('description:', '').trim()

                    break
                }

                case (Item.startsWith('field:') ? Item : '') : {
                    const Field = Item.replace('field:', '')
                    const Split = Field.split('&&')

                    Embed.fields.push({
                        name : Split[0].trim(),
                        value : Split[1].trim().replace('inline', ''),
                        inline : Split[1].trim().includes('inline') ? true : null
                    })

                    break
                }

                case (Item.startsWith('footer:') ? Item : '') : {
                    const Footer = Item.replace('footer:', '')
                    const Split = Footer.split('&&')

                    if (Split[1]) {
                        const Domain = (new URL(Split[1]))

                        if (!Domain || Domain.host !== 'blair.win' && Domain.host !== 'media.discordapp.net' && Domain.host !== 'cdn.discordapp.com') {
                            Split[1] = null
                        }
                    }

                    Embed.footer = {
                        text : Split[0].trim(),
                        iconURL : Split[1] ? Split[1].trim() : null
                    }

                    break
                }

                case (Item.startsWith('image:') ? Item : '') : {
                    var Image = Item.replace('image:', '').trim()

                    const Domain = (new URL(Image)) 

                    if (!Domain || Domain.host !== 'blair.win' && Domain.host !== 'media.discordapp.net' && Domain.host !== 'cdn.discordapp.com') {
                        Image = null
                    }

                    Embed.image = {
                        url : Image
                    }
                }

                case (Item.startsWith('thumbnail:') ? Item : '') : {
                    var Thumbnail = Item.replace('thumbnail:', '').trim()

                    const Domain = (new URL(Thumbnail))

                    if (!Domain || Domain.host !== 'blair.win' && Domain.host !== 'media.discordapp.net' && Domain.host !== 'cdn.discordapp.com') {
                        Thumbnail = null
                    }

                    Embed.thumbnail = {
                        url : Thumbnail
                    }

                    break
                }

                case (Item.startsWith('timestamp') ? Item : '') : {
                    Embed.timestamp = new Date()

                    break
                }

                case (Item.startsWith('color:') ? Item : '') : {
                    Color = Item.replace('color:', '').trim()

                    break
                }

                case (Item.startsWith('button:') ? Item : '') : {
                    const Button = Item.replace('button:', '')
                    const Split = Button.split('&&')
                    
                    Buttons.push(new Discord.ButtonBuilder({
                        label : Split[0].trim(),
                        url : Split[1].trim(),
                        emoji : Split[2] ? Split[2].trim() : null
                    }).setStyle('Link'))
                }
            }
        }

        var Embeds = []
        var Components = []

        if (Embed.author || Embed.title || Embed.url || Embed.description || Embed.fields.length > 0 || Embed.footer || Embed.image || Embed.thumbnail) {
            Embeds = [new Discord.EmbedBuilder(Embed).setColor(Color)]
        }

        if (Buttons.length > 0) {
            Components = [new Discord.ActionRowBuilder().addComponents(Buttons)]
        }

        return {
            content : Message.length > 0 ? Message : null,
            embeds : Embeds,
            components : Components
        }
    }
}