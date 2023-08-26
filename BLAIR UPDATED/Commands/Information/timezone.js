const Command = require('../../Structures/Base/command'), Discord = require('discord.js')

const { fetch } = require('undici'), qs = require('qs')

const commands = [
    'set',
    'list', 'all'
]

const moment = require('moment-timezone'), geo = require('geo-tz')

module.exports = class Timezone extends Command {
    constructor (bot) {
        super (bot, 'timezone', {
            description : `View a member's timezone`,
            parameters : [ 'member' ],
            syntax : '<member>',
            example : bot.owner.username,
            aliases : [ 'time', 'tz' ],
            commands : [
                {
                    name : 'timezone set',
                    description : 'Set your timezone',
                    parameters : [ 'location' ],
                    syntax : '(location)',
                    example : 'Los Angeles'
                },
                {
                    name : 'timezone list',
                    description : 'View all member timezones',
                    aliases : [ 'all' ]
                }
            ],
            module : 'Information'
        })
    }

    async execute (bot, message, args) {
        const command = String(args[0]).toLowerCase()

        if (args[0] && commands.includes(command)) {
            switch (true) {
                case (command === 'set') : {
                    try {
                        if (!args[1]) {
                            return bot.help(
                                message, this.commands[0]
                            )
                        }

                        if (args[1].toLowerCase() === 'none') {
                            bot.db.query('DELETE FROM timezone WHERE user_id = $1', {
                                bind : [
                                    message.author.id
                                ]
                            })

                            bot.approve(
                                message, `Your **timezone** has been **removed**`
                            )
                        } else {
                            const query = qs.stringify({
                                q : args.slice(1).join(' '),
                                limit : 1,
                                appid : process.env.OPENWEATHERMAP_APP_ID 
                            })

                            const results = await fetch(`http://api.openweathermap.org/geo/1.0/direct?${query}`, {
                                method : 'GET'
                            }).then((response) => response.json())

                            if (!results || results.length === 0) {
                                return bot.warn(
                                    message, `Location **${args.slice(1).join(' ')}** not found`
                                )
                            }

                            const location = geo.find(results[0].lat, results[0].lon)[0]

                            bot.db.query('INSERT INTO timezone (user_id, location) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET location = $2', {
                                bind : [
                                    message.author.id, location
                                ]
                            })

                            bot.approve(
                                message, `Your **timezone** has been set to \`${location}\``
                            )
                        }
                    } catch (error) {
                        return bot.error(
                            message, 'timezone set', error
                        )
                    }

                    break
                }

                case (command === 'list' || command === 'all') : {
                    try {
                        const timezones = await bot.db.query('SELECT * FROM timezone').then(([results]) => results), members = []

                        if (message.guild.memberCount !== message.guild.members.cache.size) {
                            await message.guild.members.fetch()
                        }

                        await Promise.all(
                            timezones.map(async (I) => {
                                const member = await message.guild.members.cache.get(I.user_id)

                                if (member) {
                                    members.push({
                                        text : `**${member.user.tag}** - ${I.location}`
                                    })
                                }
                            })
                        )

                        if (!members.length) {
                            return bot.warn(
                                message, `No members have their **timezone** set`
                            )
                        }

                        let index = 0

                        const pages = members.list(10)
                        
                        const embeds = await Promise.all(
                            pages.map((page) => {
                                const entries = page.map((I) => {                                    
                                    return `\`${++index}\` ${I.text}`
                                }).join('\n')
                                
                                return new Discord.EmbedBuilder({
                                    author : {
                                        name : message.member.displayName,
                                        iconURL : message.member.displayAvatarURL({
                                            dynamic : true
                                        })
                                    },
                                    title : 'Timezones',
                                    description : entries
                                }).setColor(bot.colors.neutral)
                            })
                        )

                        await new bot.paginator(
                            message, {
                                embeds : embeds,
                                entries : index,
                            }
                        ).construct()
                    } catch (error) {
                        return bot.error(
                            message, 'timezone list', error
                        )
                    }

                    break
                }
            }
        } else {
            try {
                const member = args[0] ? await bot.converters.member(
                    message, args.join(' '), {
                        response : true
                    }
                ) : message.member

                if (!member) {
                    return
                }

                const timezone = await bot.db.query('SELECT * FROM timezone WHERE user_id = $1', {
                    bind : [
                        member.user.id
                    ]
                }).then(([results]) => results[0])

                if (!timezone) {
                    const operator = member === message.member ? `Your **timezone** hasn't been set yet` : `**${member.user.tag}** hasn't set their **timezone**`

                    return bot.warn(
                        message, operator, {
                            text : member === message.member ? `Use \`${message.prefix}timezone set (location)\` to set it` : ''
                        }
                    )
                 }

                 const operator = member === message.member ? `Your current time is` : `**${member.user.tag}**'s current time is`

                 const time = moment(new Date()).tz(timezone.location).format('MMM DD, hh:mm A')

                 bot.neutral(
                    message, `${operator} **${time}**`
                 )
            } catch (error) {
                return bot.error(
                    message, 'timezone', error
                )
            }
        }
    }
}