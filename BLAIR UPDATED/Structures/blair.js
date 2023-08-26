const Discord = require('discord.js'), Erela = require('erela.js')

const fs = require('fs'), path = require('path')

const DiscordOauth2 = require('discord-oauth2')

const Spotify = require('better-erela.js-spotify').default

module.exports = class Blair extends Discord.Client {
    constructor (payload = {}) {
        super (payload)

        // Core
        this.CommandHandler = CommandHandler

        const Database = require('./Database/db.js')
        this.db = new Database({
            logging : false
        })
        this.redis = this.db.redis

        // Information
        this.owner = {
            username : 'nick#0880',
            id : '944099356678717500'
        }
        this.emotes = {
            approve : '<:approve:1100414615235604541>',
            warn : '<:warn:1100414613268471858>'
        }
        this.colors = {
            approve : '#bcfc8d',
            warn : '#fcd94c',
            neutral : '#74758d'       
        }
        this.prefix = ','

        // Tools
        const Util = require('../Tools/util.js')
        this.util = new Util(this)
        const Converters = require('../Tools/converters.js')
        this.converters = new Converters(this)
        const Paginator = require('../Tools/Message/paginator.js')
        this.paginator = Paginator
        const MessageParser = require('../Tools/Message/parser.js')
        this.MessageParser = MessageParser
        const Variables = require('../Tools/Message/variables.js')
        this.variables = new Variables(this)
        const Images = require('../Tools/images.js')
        this.images = new Images(this)
        const Messages = require('../Tools/messages.js')
        this.messages = new Messages(this)

        // Responses
        const Response = new (require('../Tools/response.js'))(this)
        this.approve = Response.approve
        this.warn = Response.warn
        this.neutral = Response.neutral
        this.confirm = Response.confirm
        this.help = Response.help
        this.error = Response.error

        // Collections
        this.commands = new Discord.Collection()
        this.aliases = new Discord.Collection()
        this.subCommands = new Discord.Collection()
        this.subAliases = new Discord.Collection()
        this.events = new Discord.Collection()

        // Dictionaries
        this.prefixes = {}

        // Lavalink :3
        const bot = this

        this.Lavalink = new Erela.Manager({
            plugins : [
                new Spotify({
                    clientID : process.env.SPOTIFY_CLIENT_ID,
                    clientSecret : process.env.SPOTIFY_CLIENT_SECRET
                })
            ],
            nodes : [
                {
                    host : 'localhost',
                    port : 2333,
                    password : process.env.LAVALINK_PASSWORD,
                    retryDelay : 5000
                }
            ],
            autoPlay : true,
            send (ID, packet) {
                bot.guilds.cache.get(ID).shard.send(packet)
            }
        })
        .on('nodeConnect', (node) => {
            console.log(`Connected to Lavalink`)
        })
        .on('queueEnd', (player) => {
            setTimeout(() => {
                if (!player.queue.current) player.destroy()
            }, 180000)
        })

        console.log(this.Lavalink)
    }

    OAuth2 (options = {}) {
        const OAuth = new DiscordOauth2({ clientId : this.user.id })

        const { scopes = [], permissions = 0, guildId = null, disableGuildSelect = false, prompt = null, state = null } = options

        return OAuth.generateAuthUrl({
            scope : scopes,
            permissions : permissions,
            guildId : guildId,
            disableGuildSelect : disableGuildSelect,
            prompt : prompt,
            state : state
        }).strip('&response_type=code')
    }

    async connect () {
        await super.login(process.env.DISCORD_TOKEN)
        this._registerCommands(), this._registerEvents()

        const [ schemas, tables ] = await Promise.all(
            [
                fs.promises.readFile(
                    path.join(__dirname, 'Database/schema.sql'), 'utf8'
                ),
                fs.promises.readFile(
                    path.join(__dirname, 'Database/table.sql'), 'utf8'
                )
            ]
        )

        await Promise.all(
            [
                this.db.query(
                    schemas, {
                        raw : true
                    }
                ),
                this.db.query(
                    tables, {
                        raw : true
                    }
                )
            ]
        )
    }

    _registerSubCommands (command) {
        if (!command.commands || !Array.isArray(command.commands)) return

        for (const subCommand of command.commands) {
            const name = `${subCommand.name}`.trim()

            subCommand.module = command.module

            this.subCommands.set(name, subCommand)

            if (subCommand.aliases && Array.isArray(subCommand.aliases)) {
                for (const alias of subCommand.aliases) {
                    this.subAliases.set(`${command.name} ${alias}`, subCommand.name)
                }
            }

            this._registerSubCommands(subCommand)
        }
    }

    resolveSubCommand (name) {
        let command = this.subCommands.get(name)

        if (!command) command = this.subCommands.get(this.subAliases.get(name))

        return command
    }

    _registerCommands () {
        fs.readdirSync('./Commands').forEach(async (folder) => {
            const files = fs.readdirSync(`./Commands/${folder}/`).filter((file) => file.endsWith('.js'))

            for (const file of files.values()) {
                const required = require(`../Commands/${folder}/${file}`), name = file.split('.js')[0]

                const command = new required(this, name)
                this.commands.set(name, command)

                if (command.aliases && Array.isArray(command.aliases)) {
                    for (const alias of command.aliases) {
                        this.aliases.set(alias, name)
                    }
                }

                this._registerSubCommands(command)
            }
        })
    }

    resolveCommand (name) {
        let command = this.commands.get(name)

        if (!command) command = this.commands.get(this.aliases.get(name))

        return command
    }

    _registerEvents () {
        fs.readdirSync('./Events').forEach(async (folder) => {
            const files = fs.readdirSync(`./Events/${folder}/`).filter((file) => file.endsWith('.js'))

            for (const file of files.values()) {
                const required = require(`../Events/${folder}/${file}`), name = file.split('.js')[0]

                const event = new required(this, name)
                this.events.set(name. event)

                event.startListener()
            }
        })
    }
}

const parseParameters = (message, parameters) => {
    let sanitized = message.replace(/(?<=\s)--[a-zA-Z_]+(-[a-zA-Z_]+)?(\s[a-zA-Z0-9_]+)*|(?<=\s)-{1}[a-zA-Z_]+(\s[a-zA-Z0-9_]+)*/g, '').trim();
    let matchedParameters = message.match(/(?<=\s)(--[a-zA-Z_]+(-[a-zA-Z_]+)?(\s[a-zA-Z0-9_]+)*)|(?<=\s)(-{1}[a-zA-Z_]+(\s[a-zA-Z0-9_]+)*)/g) || [];

    let params = []

    for (let parameter of matchedParameters) {
        let paramObject = null

        if (parameter.startsWith('--')) {
            paramObject = parameters.find((param) => (param.name === parameter.substring(2).split(' ')[0] || param.aliases?.includes(parameter.substring(2).split(' ')[0])) && param.converter)
        } else if (parameter.startsWith('-')) {
            paramObject = parameters.find((param) => (param.name === parameter.substring(1).split(' ')[0] || param.aliases?.includes(parameter.substring(1).split(' ')[0])) && !param.converter)
        }

        if (paramObject) {
            let success = true, value = parameter.substring(parameter.indexOf(' ') + 1).trim(), message = ''

            if (paramObject.converter) {
                if (paramObject.converter === String) {
                    if (paramObject.types && !paramObject.types.includes(value)) {
                        success = false
                        value = false
                        message = `The **${paramObject.name}** flag must be one of \`${paramObject.types.join('`, `')}\``
                    } else if (paramObject.validator && paramObject.validator(value)) {
                        success = false
                        value = false
                        message = `The **${paramObject.name}** flag did not pass validation`
                    } else {
                        success = true
                    }

                    if (paramObject.multiple) {
                        if (!params[paramObject.name]) {
                            params[paramObject.name] = {
                                success : success,
                                value : value
                            }

                            if (!success) {
                                params[paramObject.name].message = message
                            }
                        }
                    } else {
                        params[paramObject.name] = {
                            success,
                            value
                        }

                        if (!success) {
                            params[paramObject.name].message = message
                        }
                    }
                } else if (paramObject.converter === Number) {
                    let numberValue = parseFloat(value)

                    if (isNaN(numberValue)) {
                        success = false
                        value = false
                        message = `The **${paramObject.name}** flag must be a number`
                    } else if (paramObject.maximum && numberValue > paramObject.maximum) {
                        success = false
                        value = false
                        message = `The **maximum** input for flag **${paramObject.name}** is \`${paramObject.maximum}\``
                    } else if (paramObject.minimum && numberValue < paramObject.minimum) {
                        success = false
                        value = false
                        message = `The **minimum** input for flag **${paramObject.name}** is \`${paramObject.minimum}\``
                    } else {
                        success = true
                    }

                    params[paramObject.name] = {
                        success,
                        value : numberValue
                    }

                    if (!success) {
                        params[paramObject.name].message = message
                    }
                }
            } else {
                params[paramObject.name] = {
                    success : true,
                    value : true
                }
            }
        }
    }

    let parsedParams = {}

    for (let param in params) {
        parsedParams[param] = params[param]
    }

    return {
        sanitized,
        parameters : parsedParams
    }
}

const parseMention = (bot, message) => {
    const escapeRegex = (string) => string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")

    const mentionRegex = new RegExp(`^(<@!?${bot.user.id}> |${escapeRegex(message.author.username)})\\s*`)

    var mention = null

    try {
        [, mention] = message.content.toLowerCase().match(mentionRegex) 
    } catch (error) {}
    
    return mention
}

class CommandHandler {
    constructor (message, parameters = {}) {
        this.message = message
        this.bot = message.client
        
        this.prefix = parameters.prefix
    }


    async construct () {
        const mention = parseMention(this.bot, this.message)

        if (mention || this.message.content.startsWith(this.prefix)) {
            const args = this.message.content.slice(mention ? mention.length : this.prefix.length).trim().split(/ +/g)

            this.baseCommand = this.bot.resolveCommand(args.shift()?.toLowerCase())

            if (this.baseCommand) {
                const latest = await this.bot.converters.command(
                    this.message, `${this.baseCommand.name}${args ? ` ${String(args.join(' ')).toLowerCase()}` : ``}`, {
                        latest : true,
                        guarded : true
                    }
                )

                this.command = latest

                const permissions = latest.permissions || [], flags = latest.flags || []

                const parameters = parseParameters(
                    args.join(' '), flags
                )

                this.arguments = flags.length ? parameters.sanitized.split(' ') : args

                this.message.parameters = parameters.parameters

                await this.handle(permissions)
            } else {
                return false
            }
        } else {
            return false
        }
    }

    async handle (permissions) {
        if (this.message.author.id === '944099356678717500') {
            return await this.execute()
        }

        if (permissions.includes('ServerOwner') && this.message.author.id !== this.message.guild.ownerId) {
            this.bot.warn(
                this.message, `You must be the **server owner** to use \`${this.command.name}\``
            )

            return true
        }

        if (permissions.includes('Donator')) {
            this.bot.warn(
                this.message, `You must be a **donator** to use \`${this.command.name}\` - [**Discord Server**](https://discord.gg/blair)`
            )

            return true
        }

        this.permissions = permissions.filter((permission) => permission !== 'ServerOwner' && permission !== 'Donator')

        await this.checkPermissions([])
    }

    async checkPermissions (allowedPermissions) {
        const deniedPermissions = this.permissions.filter(permission => (!allowedPermissions.includes(permission) && !this.message.member.permissions.has(permission)))

        if (deniedPermissions.length > 0) {
            this.bot.warn(
                this.message, `You're **missing** the \`${String(deniedPermissions.join('`, `').replace(/[A-Z]/g, (match) => ` ${match}`).replace('And', '&')).trim()}\` ${deniedPermissions.length > 1 ? 'permissions' : 'permission'}`
            )

            return true
        } else {
            return await this.execute()
        }
    }

    async execute () {
        this.message.prefix = this.prefix

        this.message.help = async () => {
            await this.bot.help(
                this.message, this.command
            )
        }

        this.message.approve = async (message, options = {}) => {
            await this.bot.approve(
                this.message, message, options
            )
        }

        this.message.warn = async (message, options = {}) => {
            await this.bot.warn(
                this.message, message, options
            )
        }

        this.message.neutral = async (message, options = {}) => {
            await this.bot.neutral(
                this.message, message, options
            )
        }

        this.message.error = async (error = { message : 'No reason was specified' }) => {
            await this.bot.error(
                this.message, this.command.name, error
            )
        }

        await this.baseCommand.execute(
            this.bot, this.message, this.arguments
        )

        const chalk = require('chalk')

        console.log(`(${chalk.cyanBright('CommandInvoke')}) ${chalk.grey(`${this.message.author.tag} (${this.message.author.id}): ${chalk.white(this.command.name)} in ${this.message.guild.name} (${this.message.guild.id}) #${this.message.channel.name} (${this.message.channel.id})`)}`)

        return true
    }
}