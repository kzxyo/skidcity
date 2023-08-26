const Client = require('./Structures/blair.js'), Discord = require('discord.js')

console.clear()
require('dotenv/config')

const bot = new Client({
    shards : 'auto',
    allowedMentions : {
        repliedUser : false,
        parse : [
            'users'
        ]
    },
    presence : {
        activities : [
            {
                name : 'discord.gg/blair',
                type : Discord.ActivityType.Competing,
            }
        ],
        status : 'online'
    },
    intents : [
        Discord.GatewayIntentBits.Guilds,
        Discord.GatewayIntentBits.GuildMembers,
        Discord.GatewayIntentBits.GuildVoiceStates,
        Discord.GatewayIntentBits.GuildMessages,
        Discord.GatewayIntentBits.GuildEmojisAndStickers,
        Discord.GatewayIntentBits.GuildMessageReactions,
        Discord.GatewayIntentBits.MessageContent
    ],
    partials : [
        Discord.Partials.GuildMember,
        Discord.Partials.Message,
        Discord.Partials.Reaction,
        Discord.Partials.User
    ],
    failIfNotExists : false,
    ws : {
        properties : {
            browser : 'Discord iOS'
        }
    }
})

bot.connect()

process.on('unhandledRejection', (error, reason) => {
    console.error(
        error, 'Unhandled Rejection at Promise', reason
    )
})

process.on('uncaughtException', (error) => {
    console.error(
        error, 'Uncaught Exception thrown'
    )
})

Object.defineProperty(
    String.prototype, 'strip', {
        value : function (str) {
            return this.replaceAll(str, '')
        }
    }
)

Object.defineProperty(
    Array.prototype, 'list', {
        value : function (n) {
            return Array.from(
                Array(Math.ceil(this.length / n)),
                (_, i) => this.slice(i * n, i * n + n)
            )
        }
    }
)
