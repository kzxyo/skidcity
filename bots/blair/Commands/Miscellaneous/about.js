const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')
const { ActionRowBuilder } = require('discord.js')
const { ButtonBuilder } = require('discord.js')

module.exports = class About extends Command {
    constructor (Client) {
        super (
            Client, 'about', {
                Aliases : [ 'botinfo', 'blairinfo' ]
            }
        )
    }

    async Invoke (Client, Message, Arguments) {
        const Days = Math.floor(Client.uptime / 86400000)
        const Hours = Math.floor(Client.uptime / 3600000) % 24
        const Minutes = Math.floor(Client.uptime / 60000) % 60
        const Seconds = Math.floor(Client.uptime / 1000) % 60

        var Total = 0, Online = 0, OnlinePresence = 0

        for (const Guild of Client.guilds.cache.values()) {
            Online = Online + Guild.members.cache.filter(Member => Member.presence && Member.presence.status !== 'offline').size
            OnlinePresence = OnlinePresence + Guild.members.cache.filter(Member => Member.presence && Member.presence.activities[0]).size
            Total = Total + Guild.memberCount
        }

        Message.channel.send({
            embeds : [
                new EmbedBuilder({
                    author : {
                        name : Client.user.username,
                        iconURL : Client.user.displayAvatarURL()
                    },
                    description : `Developer: **nick#0407**, Memory: **${(process.memoryUsage().rss / 1024 / 1024).toFixed(2)}MB**, Commands: **${Client.Commands.size}**.`,
                    fields : [
                        {
                            name : `Cached Statistics (${parseInt(Client.guilds.cache.size).toLocaleString()} Guilds)`,
                            value : `Members: **${parseInt(Total).toLocaleString()}** total (**${parseInt(Online).toLocaleString()}** online & **${parseInt(OnlinePresence).toLocaleString()}** online with presence)\nChannels: **${parseInt(Client.channels.cache.size).toLocaleString()}** total (**${parseInt(Client.channels.cache.filter(Channel => Channel.type === 0).size).toLocaleString()}** text, **${parseInt(Client.channels.cache.filter(Channel => Channel.type === 2).size).toLocaleString()}** voice & **${parseInt(Client.channels.cache.filter(Channel => Channel.type === 4).size).toLocaleString()}** category)`
                        }
                    ],
                    footer : {
                        text : `Websocket: ${Client.ws.ping}ms, Uptime: ${Days ? `${Days} ${Days === 1 ? 'day' : 'Days'}, ${Hours} ${Hours === 1 ? 'hour' : 'Hours'} and ${Minutes} ${Minutes === 1 ? 'minute' : 'Minutes'}` : Hours ? `${Hours} ${Hours === 1 ? 'hour' : 'Hours'}, ${Minutes} ${Minutes === 1 ? 'minute' : 'Minutes'} and ${Seconds} ${Seconds === 1 ? 'second' : 'Seconds'}` : Minutes ? `${Minutes} ${Minutes === 1 ? 'minute' : 'Minutes'} and ${Seconds} ${Seconds === 1 ? 'second' : 'Seconds'}` : `${Seconds} ${Seconds === 1 ? 'second' : 'Seconds'}` }`
                    }
                }).setColor(Client.Color)
            ]
        })
    }
}