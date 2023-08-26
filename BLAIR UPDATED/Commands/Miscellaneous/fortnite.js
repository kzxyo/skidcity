const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const commands  =[
    'lookup', 'search', 'find',
    'shop', 'store'
]

const { fetch } = require('undici')

module.exports = class Fortnite extends Command {
    constructor (bot) {
        super (bot, 'fortnite', {
            description : 'Fortnite cosmetic-related commands',
            syntax : '(subcommand) <args>',
            example : 'lookup Renegade Raider',
            aliases : [ 'fort', 'fn' ],
            commands : [
                {
                    name : 'fortnite lookup',
                    description : 'Search for a cosmetic w/ occurences',
                    parameters : [ 'cosmetic' ],
                    syntax : '(cosmetic)',
                    example : 'Renegade Raider',
                    aliases : [ 'search', 'find' ]
                },
                {
                    name : 'fortnite shop',
                    description : 'Get the current Fortnite item shop',
                    aliases : [ 'store' ]
                }
            ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        const command = String(args[0]).toLowerCase()

        if (!args[0] || !commands.includes(command)) {
            return bot.help(
                message, this
            )
        }

        switch (true) {
            case (command === 'lookup' || command === 'search' || command === 'find') : {
                try {
                    if (!args[1]) {
                        return bot.help(
                            message, this.commands[0]
                        )
                    }

                    const results = await fetch(`https://fortnite-api.com/v2/cosmetics/br/search?matchMethod=contains&name=${encodeURIComponent(args.slice(1).join(' '))}`, {
                        method : 'GET'
                    }).then((response) => response.json()).catch((error) => {
                        return bot.warn(
                            message, `Bad response (\`${error.response.status}\`) from the **API**`
                        )
                    })

                    if (results.status !== 200) {
                        return bot.warn(
                            message, `Cosmetic **${args.slice(1).join(' ')}** not found`
                        )
                    }

                    const { name, description, type, introduction, added, shopHistory } = results.data

                    const occurrences = []

                    if (shopHistory) {
                        const dates = shopHistory.sort((a, b) => new Date(b) - new Date(a)).slice(0, 5).map((date) => new Date(date).getTime())

                        await Promise.all(dates.map((date) => {
                            date = Math.floor(date / 1000)

                            occurrences.push(`> <t:${date}:D> (<t:${date}:R>)`)
                        }))
                    }

                    const results2 = await fetch(`https://fnbr.co/api/images?search=${encodeURI(name)}&limit=${encodeURI(1)}&type=${encodeURI(type.value)}`, {
                        method : 'GET',
                        headers : {
                            'x-api-key' : process.env.FNBR_API_KEY
                        }
                    }).then((response) => response.json())

                    console.log(results2.data)

                    const { images, readableType } = results2.data[0]

                    const date = new Date(added)

                    const dateToCompare = new Date('2019-11-20')

                    const malformedDate = date.getFullYear() === dateToCompare.getFullYear() && date.getMonth() === dateToCompare.getMonth() && date.getDate() === dateToCompare.getDate()

                    message.channel.send({
                        embeds : [
                            new Discord.EmbedBuilder({
                                author : {
                                    name : message.member.displayName,
                                    iconURL : message.member.displayAvatarURL({
                                        dynamic : true
                                    })
                                },
                                title : `${name}`,
                                url : `https://fnbr.co/${type.value}/${name.replaceAll(' ', '-')}`,
                                description : `${description}${introduction ? introduction.text ? `\n> ${introduction.text}` : '' : ''}`,
                                fields : occurrences.length ? [
                                    {
                                        name : `Occurrence${occurrences.length > 1 ? 's' : ''}`,
                                        value : `${occurrences.join('\n')}`
                                    }
                                ] : [],
                                footer : {
                                    text : `${readableType}${!malformedDate ? ` | Added on` : ''}`
                                },
                                thumbnail : {
                                    url : images.icon
                                },
                                timestamp : malformedDate ? null : date
                            }).setColor(bot.colors.neutral)
                        ]
                    })
                } catch (error) {
                    return bot.error(
                        message, 'fortnite lookup', error
                    )
                }

                break
            }

            case (command === 'shop' || command === 'store') : {
                try {
                    const date = new Date(), day = date.getDate(), month = date.getMonth() + 1, year = date.getFullYear(), format = `${day}-${month}-${year}`

                    message.channel.send({
                        embeds : [
                            new Discord.EmbedBuilder({
                                author : {
                                    name : message.member.displayName,
                                    iconURL : message.member.displayAvatarURL({
                                        dynamic : true
                                    })
                                },
                                title : 'Fortnite Item Shop',
                                image : {
                                    url : `https://bot.fnbr.co/shop-image/fnbr-shop-${format}.png`
                                }
                            }).setColor(bot.colors.neutral)
                        ]
                    })
                } catch (error) {
                    return bot.error(
                        message, 'fortnite shop', error
                    )
                }

                break
            }
        }
    }
}