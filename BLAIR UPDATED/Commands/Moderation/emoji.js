const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const twemoji = require('@discordapp/twemoji'), twemojiParser = require('twemoji-parser'), parser = require('discord-emojis-parser')
const sharp = require('sharp'), axios = require('axios')
const crypto = require('crypto')

const commands = [
    'add', 'create', 'copy',
    'addmany', 'am',
    'list', 'all',
    'remove', 'rm', 'delete', 'del'
]

module.exports = class Emoji extends Command {
    constructor (bot) {
        super (bot, 'emoji', {
            description : 'Enlarge an emoji',
            parameters : [ 'emoji' ],
            syntax : '(subcommand) <args>',
            example : '🔥',
            aliases : [ 'emote', 'e' ],
            commands : [
                {
                    name : 'emoji add',
                    description : 'Add an emoji to the server',
                    permissions : [ 'ManageEmojisAndStickers' ],
                    parameters : [ 'image' ],
                    syntax : '(emoji or url) <name>',
                    example : '.../attachments/... cool',
                    aliases : [ 'create', 'copy' ]
                },
                {
                    name : 'emoji addmany',
                    description : 'Bulk add emojis to the server',
                    permissions : [ 'ManageEmojisAndStickers' ],
                    parameters : [ 'emojis' ],
                    syntax : '(emojis)',
                    example : ':emoji1: :emoji2:',
                    aliases : [ 'am' ]
                },
                {
                    name : 'emoji list',
                    description : 'View all emojis in the server',
                    aliases : [ 'all' ]
                },
                {
                    name : 'emoji remove',
                    description : 'Remove an emoji from the server',
                    permissions : [ 'ManageEmojisAndStickers' ],
                    parameters : [ 'emoji' ],
                    syntax : '(emoji)',
                    example : ':cool: ',
                    aliases : [ 'rm', 'delete', 'del' ],
                    commands : [
                        {
                            name : 'emoji remove duplicates',
                            description : 'Sort and remove duplicate emojis',
                            permissions : [ 'ManageEmojisAndStickers' ],
                            aliases : [ 'dupes' ]
                        }
                    ]
                },
                {
                    name : 'emoji rename',
                    description : 'Rename an emoji in the server',
                    permissions : [ 'ManageEmojisAndStickers' ],
                    parameters : [ 'emoji', 'name' ],
                    syntax : '(emoji) (name)',
                    example : ':cool: coolest',
                    aliases : [ 'name' ]
                }
            ],
            module : 'Moderation'
        })
    }

    async execute (bot, message, args) {
        const command = String(args[0]).toLowerCase()

        if (!args[0]) {
            return bot.help(
                message, this
            )
        }

        if (commands.includes(command)) {
            switch (true) {
                case (command === 'add' || command === 'create' || command === 'copy') : {
                    try {
                        if (!args[1] && !message.attachments.first()) {
                            return bot.help(
                                message, this.commands[0]
                            )
                        }

                        const image = await bot.converters.attachment(
                            message, args[1], {
                                types : [
                                    'attachment', 'emote', 'sticker'
                                ]
                            }
                        )

                        if (!image) {
                            return bot.warn(
                                message, `Invalid **image**`
                            )
                        }

                        let name = image.isArgs ? args.slice(2).join(' ') : args.slice(1).join(' ')

                        if (!name) {
                            if (!image.name) {
                                return bot.warn(
                                    message, `Please specify a **name** for the emoji`
                                )
                            }

                            name = image.name.slice(0, 30)
                        }

                        const timeout = new Promise((resolve, reject) => {
                            const ID = setTimeout(() => {
                                clearTimeout(ID)

                                reject(new Error('Timed Out'))
                            }, 5000)
                        })

                        try {
                            const emoji = await Promise.race([
                                message.guild.emojis.create({
                                    attachment : image.url,
                                    name : name,
                                    reason : `${message.author.tag}: Added Emoji`
                                }),
                                timeout
                            ])

                            bot.approve(
                                message, `Added [**${emoji.name}**](https://cdn.discordapp.com/emojis/${emoji.id}${emoji.animated ? '.gif' : '.png'}) to the server`
                            )
                        } catch (error) {
                            return bot.warn(
                                message, `Failed to create the **emoji** - Timed out`
                            )
                        }
                    } catch (error) {
                        return bot.error(
                            message, 'emoji add', error
                        )
                    }

                    break
                }

                case (command === 'addmany' || command === 'am') : {
                    try {
                        if (!args[1]) {
                            return bot.help(
                                message, this.commands[1]
                            )
                        }

                        const emojis = message.content.match(/<a:.+?:\d+>|<:.+?:\d+>/g)

                        if (!emojis || !emojis.length) {
                            return bot.help(
                                message, this.commands[1]
                            )
                        }

                        const reaction = await message.react('⚙️')

                        const timeout = new Promise ((resolve, reject) => {
                            const ID = setTimeout(() => {
                                clearTimeout(ID)

                                reject(new Error('Timed Out'))
                            }, 20000)
                        })

                        const result = Promise.all(
                            emojis.map(async (emoji) => {
                                return new Promise (async (resolve) => {
                                    const emote = await Discord.parseEmoji(emoji)

                                    if (emote.id) {
                                        await message.guild.emojis.create({
                                            attachment : new Discord.CDN().emoji(emote.id, emote.animated),
                                            name : emote.name,
                                            reason : message.author.tag
                                        }).catch((error) => {
                                            resolve(false)
                                        }).then(() => {
                                            resolve(true)
                                        })
                                    } else {
                                        resolve(false)
                                    }
                                })
                            })
                        )

                        try {
                            const promise = await Promise.race([result, timeout])

                            reaction.users.remove(bot.user.id)
                            
                            const success = promise.filter((a) => a === true), failure = promise.filter((a) => a === false)

                            bot.approve(
                                message, `Added **${success.length} emojis** to the server`, {
                                    text : failure.length > 0 ? `\`${failure.length}\` failed` : null
                                }
                            )
                        } catch (error) {
                            reaction.users.remove(bot.user.id)

                            return bot.warn(
                                message, `Failed to create **multiple emojis** - Timed out`
                            )
                        }
                    } catch (error) {
                        return bot.error(
                            message, 'emoji addmany', error
                        )
                    }

                    break
                }

                case (command === 'list' || command === 'all') : {
                    try {
                        let index = 0

                        const embeds = await Promise.all(
                            message.guild.emojis.cache.map((emoji) => emoji).list(10).map((page) => {
                                const entries = page.map((I) => {
                                    return `\`${++index}\` ${I} [**${I.name}**](https://cdn.discordapp.com/emojis/${I.id}${I.animated ? '.gif' : '.png'}) (\`${I.id}\`)`
                                }).join('\n')
                                
                                return new Discord.EmbedBuilder({
                                    author : {
                                        name : message.member.displayName,
                                        iconURL : message.member.displayAvatarURL({
                                            dynamic : true
                                        })
                                    },
                                    title : `Emojis in ${message.guild.name}`,
                                    description : entries
                                }).setColor(bot.colors.neutral)
                            })
                        )

                        await new bot.paginator(
                            message, {
                                embeds : embeds, entries : index
                            }
                        ).construct()
                    } catch (error) {
                        return bot.error(
                            message, 'emoji list', error
                        )
                    }

                    break
                }

                case (command === 'remove' || command === 'rm' || command === 'delete' || command === 'del') : {
                    const subCommand = String(args[1]).toLowerCase(), subCommands = [ 'duplicates', 'dupes' ]

                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[3]
                        )
                    }

                    if (subCommands.includes(subCommand)) {
                        switch (true) {
                            case (subCommand === 'duplicates' || subCommand === 'dupes') : {
                                try {
                                    const reaction = await message.react('⚙️')

                                    const unique = []

                                    for (const emoji of message.guild.emojis.cache.values()) {
                                        const image = await axios({
                                            method : 'GET',
                                            url : emoji.url,
                                            responseType : 'arraybuffer'
                                        }).then((response) => response.data)

                                        const data = Buffer.from(image)

                                        const hash = crypto.createHash('sha256').update(data).digest('hex').substring(0, 16)

                                        const existing = unique.find((e) => e.hash === hash)

                                        if (existing) {
                                            existing.emojis.push(
                                                {
                                                    id : emoji.id,
                                                    name : emoji.name,
                                                    url : emoji.url
                                                }
                                            )
                                        } else {
                                            unique.push(
                                                {
                                                    hash : hash,
                                                    emojis : [
                                                        {
                                                            id : emoji.id,
                                                            name : emoji.name,
                                                            url : emoji.url
                                                        }
                                                    ]
                                                }
                                            )
                                        }
                                    }

                                    const sorted = unique.filter((e) => e.emojis.length > 1)

                                    if (!sorted.length) {
                                        reaction.users.remove(bot.user.id)

                                        return bot.warn(
                                            message, `There are no **duplicate emojis** in this server`
                                        )
                                    }

                                    reaction.users.remove(bot.user.id)

                                    let index = 0

                                    const embeds = await Promise.all(
                                        sorted.list(9).map(async (page) => {
                                            const fields = []

                                            await Promise.all(
                                                page.map(async (I) => {
                                                    fields.push(
                                                        {
                                                            name : I.hash,
                                                            value : `> ${I.emojis.map((emoji) => `<:${emoji.name}:${emoji.id}> [\`:${emoji.name}:\`](${emoji.url})`).join('\n> ')}`,
                                                            inline : true
                                                        }
                                                    )
                                                })
                                            )

                                            return new Discord.EmbedBuilder({
                                                author : {
                                                    name : message.member.displayName,
                                                    iconURL : message.member.displayAvatarURL({
                                                        dynamic : true
                                                    })
                                                },
                                                title : 'Duplicate Emojis',
                                                fields : fields
                                            }).setColor(bot.colors.neutral)
                                        })
                                    )

                                    const options = sorted.map(({ emojis }) => {
                                        const { id, name } = emojis[0]

                                        return {
                                            label : name,
                                            value : id,
                                            emoji : id
                                        }
                                    }).slice(0, 25)

                                    const SelectMenu = new Discord.StringSelectMenuBuilder()
                                    .setCustomId('remove-duplicates')
                                    .setPlaceholder('Select which emojis to keep..')
                                    .setMinValues(0)
                                    .setMaxValues(options.length)
                                    .addOptions(options)

                                    await new bot.paginator(
                                        message, {
                                            embeds : embeds,
                                            components : [
                                                new Discord.ActionRowBuilder({
                                                    components : [
                                                        SelectMenu
                                                    ]
                                                })
                                            ]
                                        }
                                    ).construct()
                                } catch (error) {
                                    return bot.error(
                                        message, 'emoji remove duplicates', error
                                    )
                                }
                            }
                        }
                    } else {
                        try {

                        } catch (error) {
                            return bot.error(
                                message, 'emoji remove', error
                            )
                        }
                    }

                    break
                }
            }
        } else {
            try {
                if (!args[0]) {
                    return message.help()
                }
    
                let emoji
    
                const emote = Discord.parseEmoji(args[0]) 
    
                if (emote.id) {
                    emoji = {
                        emote : true,
                        url : new Discord.CDN().emoji(emote.id, emote.animated),
                        isGIF : emote.animated
                    }
                } else {
                    const parsedEmoji = parser.parse(args[0])
    
                    if (!parsedEmoji.length) {
                        return bot.warn(`Invalid **emote**`)
                    }
    
                    emoji = {
                        emote : false,
                        url : parsedEmoji[0].svg
                    }
                }
    
                if (emoji.emote) {
                    if (emoji.isGIF) {
                        message.channel.send({
                            files : [
                                new Discord.AttachmentBuilder(
                                    emoji.url, {
                                        name : 'emote.gif'
                                    }
                                )
                            ]
                        })
                    } else {
                        const PNG = await axios({
                            method : 'GET',
                            url : emoji.url,
                            responseType : 'arraybuffer'
                        }).then((response) => response.data)
    
                        const Buffer = await sharp(PNG).resize(512, 512).toBuffer()
    
                        message.channel.send({
                            files : [
                                new Discord.AttachmentBuilder(
                                    Buffer, {
                                        name : 'emote.png'
                                    }
                                )
                            ]
                        })
                    }
                } else {
                    const SVG = await axios({
                        method : 'GET',
                        url : emoji.url,
                        responseType : 'arraybuffer'
                    }).then((response) => response.data)
    
                    const PNGBuffer = await sharp(SVG).resize(627, 627).png().toBuffer()
    
                    message.channel.send({
                        files : [
                            new Discord.AttachmentBuilder(
                                PNGBuffer, {
                                    name : 'emoji.png'
                                }
                            )
                        ]
                    })
                }
            } catch (error) {
                return bot.error(
                    message, 'emoji', error
                )
            }
        }
    }
}