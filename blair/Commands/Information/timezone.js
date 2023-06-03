const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

const Moment = require('moment-timezone')

const Commands = [ 'set', 'view' ]

const { find } = require('geo-tz')
const Phin = require('phin')

module.exports = class TimeZone extends Command {
    constructor (Client) {
        super (Client, 'timezone', {
            Aliases : [ 'time', 'tz' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const Command = String(Arguments[0]).toLowerCase()

        if (Arguments[0] && Commands.includes(Command)) {
            switch (Command) {
                case ('set') : {
                    try {
                        const Location = String(Arguments.slice(1).join('-')).toLowerCase()

                        if (!Arguments[1]) {
                            return new Client.Help(
                                Message, {
                                    About : 'Set your timezone.',
                                    Syntax : 'timezone set (Location)'
                                }
                            )
                        }

                        const Search = await Phin({
                            url : `http://api.openweathermap.org/geo/1.0/direct?q=${Location}&limit=1&appid=bb436a823ae4337d389eb9e2622aba21`,
                            method : 'GET',
                            parse : 'json'
                        })

                        if (!Search || Search.body.length === 0) {
                            return new Client.Response(
                                Message, `Couldn't find a **Location** or **City** for your arguments.`
                            )
                        }

                        const TimeZone = find(Search.body[0].lat, Search.body[0].lon)[0]

                        Client.Database.query(`SELECT * FROM timezones WHERE user_id = ${Message.author.id}`).then(async ([Results]) => {
                            if (Results.length > 0) {
                                Client.Database.query(`UPDATE timezones SET timezone = '${TimeZone}' WHERE user_id = ${Message.author.id}`).catch((Error) => console.error(Error))
                            } else {
                                Client.Database.query(`INSERT INTO timezones (user_id, timezone) VALUES (${Message.author.id}, '${TimeZone}')`).catch((Error) => console.error(Error))
                            }

                            return new Client.Response(
                                Message, `Your timezone has been set as **${TimeZone}**.`
                            )
                        })
                    } catch (Error) {
                        return new Client.Error(
                            Message, 'timezone set', Error
                        )
                    }

                    break
                }

                case ('view') : {
                    try {

                    } catch (Error) {
                        return new Client.Error(
                            Message, 'timezone view', Error
                        )
                    }
                }
            }
        } else {
            try {
                const Member = await Arguments[0] ? Message.guild.members.cache.get(Arguments[0]) || Message.guild.members.cache.find(Member => String(Member.user.username).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(Member.user.tag).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase()) || String(Member.displayName).toLowerCase().includes(String(Arguments.join(' ')).toLowerCase())) || Message.mentions.members.last() : Message.member

                if (!Member) {
                    return new Client.Response(
                        Message, `Couldn't find a **Member** with that username.`
                    )
                }

                Client.Database.query(`SELECT * FROM timezones WHERE user_id = ${Member.id}`).then(async ([Results]) => {
                    if (Results.length === 0) {
                        return new Client.Response(
                            Message, `${Member === Message.member ? `You haven't set your **Location** - Set it with \`timezone set\` and then try again.` : `Member **${Member.user.tag}** has not set their timezone.`}`
                        )
                    }

                    const Time = Moment(new Date()).tz(Results[0].timezone).format('MMMM Do, h:mm A')

                    return new Client.Response(
                        Message, `${Member === Message.member ? `Your current time is` : `Member **${Member.user.tag}**'s current time is`} **${Time}**.`
                    )
                })
            } catch (Error) {
                return new Client.Error(
                    Message, 'timezone', Error
                )
            }
        }
    }
}