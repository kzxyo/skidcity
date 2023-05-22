const Database = require('../Other/Database.js')
const Discord = require('discord.js')
const fs = require('fs')

module.exports = class Client extends Discord.Client {
    constructor () {
        super ({
            intents : 131071,
            partials : [
                Discord.Partials.Message,
                Discord.Partials.Reaction
            ],
            allowedMentions : {
                parse : [
                    'everyone', 'users', 'roles'
                ]
            }
        })

        this.Client = this

        this.Color = '#c6bfc6'
        this.DefaultPrefix = '.'


        this.Database = new Database()

        this.Commands = new Discord.Collection()
        this.Aliases = new Discord.Collection()
        this.Events = new Discord.Collection()
        this.SubCommands = new Discord.Collection()
        this.SubAliases = new Discord.Collection()

        this.AFK = new Discord.Collection()

        this.Structure = require('../Structure.js')

        this.Response = require('../../Util/Embeds/Response.js')
        this.Error = require('../../Util/Client/Error.js')
        this.Help = require('../../Util/Embeds/Help.js')

        this.EmbedParser = require('../../Util/Client/EmbedParser.js')
        this.Variables = require('../../Util/Client/Variables.js')
        
        this.Administrators = [
            '944099356678717500', // Me
            '671744161107410968', // Mar
        ]

        this.Emotes = {
            Lock : '<:bLock:1054590104183783444>',
            Unlock : '<:bUnlock:1054590102774493226>',
            Increase : '<:bPlus:1054590107920912394>',
            Decrease : '<:bMinus:1054590106729726022>',
            Note : '<:bNote:1054603594042716160>',
            Hide : '<:bHide:1054608178261790831>',
            Reveal : '<:bReveal:1054604574750683166>',
            Initialize : '<:bComputer:1054590105353981982>',
            Hammer : '<:bHammer:1054600916453572630>',
            Microphone : '<:bMicrophone:1054590102128570378>'
        }
    }

    async Start (Token) {
        super.login(Token).then(() => {
            console.log('Connected (Discord)')
        })

        setTimeout(() => {
            this.user.setActivity('blair.win/discord', {
                type : Discord.ActivityType.Watching
            })
        }, 30000)

        setInterval(() => {
            this.user.setActivity('blair.win/discord', {
                type : Discord.ActivityType.Watching
            })
        }, 600000)

        this.LoadCommands(); this.LoadEvents()
    }

    async CreateTimestamp (Timestamp) {
        var delta = Math.abs(new Date() - Timestamp) / 1000
        let days = Math.floor(delta / 86400); delta -= days * 86400;  
        let hours = Math.floor(delta / 3600) % 24; 
        delta -= hours * 3600; 
        let minutes = Math.floor(delta / 60) % 60; delta -= minutes * 60; 
        let seconds = delta % 60; seconds < 10 ? seconds = Number(seconds.toString().slice(0, 1)) : seconds = Number(seconds.toString().slice(0, 2))

        return `${days === 0 ? hours === 0 ? minutes === 0 ? `${seconds} ${seconds === 1 ? 'second' : 'seconds'}` : `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} and ${seconds} ${seconds === 1 ? 'second' : 'seconds'}` : `${hours} ${hours === 1 ? 'hour' : 'hours'}, ${minutes} ${minutes === 1 ? 'minute' : 'minutes'} and ${seconds} ${seconds === 1 ? 'second' : 'seconds'}` : `${days} ${days === 1 ? 'day' : 'days'}, ${hours} ${hours === 1 ? 'hour' : 'hours'} and ${minutes} ${minutes === 1 ? 'minute' : 'minutes'}`}`
    }

    GetCommand (Input) {
		var Command = this.Commands.get(Input)

		if (!Command) Command = this.Commands.get(this.Aliases.get(Input))

		return Command
	}

    LoadCommands () {
        fs.readdirSync('./Commands').forEach(async (Directory) => {
            const Files = fs.readdirSync(`./Commands/${Directory}/`).filter((File) => File.endsWith('.js'))

            for (const File of Files.values()) {
                const CommandBuilder = require(`../../Commands/${Directory}/${File}`), Name = File.split('.js')[0]

				const Command = new CommandBuilder(this, Name)
				this.Commands.set(Name, Command)

                if (Command.Aliases && Command.Aliases && Array.isArray(Command.Aliases)) {
					for (const Alias of Command.Aliases) {
						this.Aliases.set(Alias, Name)
					}
				}

                if (Command.Commands && Array.isArray(Command.Commands)) {
					for (const SubCommand of Command.Commands) {
						this.SubCommands.set(SubCommand.Name, SubCommand)

						if (SubCommand.Aliases && Array.isArray(SubCommand.Aliases)) {
							for (const Alias of SubCommand.Aliases) {
								this.SubAliases.set(`${Name} ${Alias}`, SubCommand.Name)
							}
						}
					}
				}
            }
        })
    }

    LoadEvents () {
        fs.readdirSync('./Events').forEach(async (Directory) => {
            const Files = fs.readdirSync(`./Events/${Directory}/`).filter((File) => File.endsWith('.js'))

            for (const File of Files.values()) {
                const EventBuilder = require(`../../Events/${Directory}/${File}`), Label = File.split('.js')[0]

                const Event = new EventBuilder(this, Label)
                this.Events.set(Label, Event)

                Event.StartListener()
            }
        })
    }

    async ReloadCommand (CommandName) {
        fs.readdirSync('./Source/Commands').forEach(async (Directory) => {
			const Commands = fs.readdirSync(`./Source/Commands/${Directory}/`).filter((file) => file.endsWith('.js'))

			for (const File of Commands.values()) {
				const Name = File.split('.js')[0]

                if (Name === String(CommandName).toLowerCase()) {
                    delete require.cache[require.resolve(`../../Commands/${Directory}/${File}`)]

                    this.Commands.delete(Name)

                    const Command = require(`../../Commands/${Directory}/${File}`)
                    const Class = new Command(this, Name)
                    this.Commands.set(Name, Class)

                    if (Class.Aliases && Class.Aliases && Array.isArray(Class.Aliases)) {
                        for (const Alias of Class.Aliases) {
                            this.Aliases.set(Alias, Name)
                        }
                    }
                }
			}
		})
    }
} 