const Event = require('../../Structures/Base/Event.js')
const { EmbedBuilder, AttachmentBuilder } = require('discord.js')

const Phin = require('phin')
const Unshorten = require('unshorten.it')

module.exports = class MessageCreate extends Event {
    constructor (Client) {
        super (Client, 'messageCreate')
    }

    async Invoke (Message) {
        if (!Message.guild || Message.author.bot) return; if (!Message.member) Message.member = await Message.guild.fetchMember(Message)

        try {
            if (String(Message.content).toLowerCase().startsWith('blair')) {
                for (const Split of Message.content.split(' ')) {
                    if ((Split.includes('vm.tiktok.com/') || Split.includes('tiktok.com/@'))) {
                        Message.channel.sendTyping()

                        try {
                            const UnshortenedURL = await Unshorten(Split)

                            const TikTok = await Phin({
                                url : 'https://www.tikwm.com/api/',
                                method : 'POST',
                                parse : 'json',
                                headers : {
                                    'accept' : 'application/json, text/javascript, */*; q=0.01',
                                    'content-type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                                    'sec-ch-ua' : '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                                    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
                                },
                                data : {
                                    url : UnshortenedURL,
                                    count : 12,
                                    cursor : 0,
                                    web : 1,
                                    hd : 1
                                }
                            })

                            if (TikTok.body.data.images) {
                                for (const Image of TikTok.body.data.images) {

                                }
                            } else {
                                try {
                                    Message.reply({
                                        files : [
                                            new AttachmentBuilder(
                                                `https://tikwm.com/${TikTok.body.data.play}`, { 
                                                    name : `blairTikTok.mp4` 
                                                }
                                            )	
                                        ],
                                        allowedMentions : { 
											repliedUser : false 
										}
                                    })
                                } catch (Error) {
                                    console.error(Error)
                                }
                            }
						} catch (Error) {
                            console.error(Error)
						}
                    }
                }
            }

            if (String(Message.content).toLowerCase().startsWith('blair clever')) {
				const AllowList = ['944099356678717500', '671744161107410968']

				if (AllowList.includes(Message.author.id)) {
					const Question = Message.content.slice('blair clever'.length).trim().split(/ +/g)

					if (Question) {
						await Phin({
							url : `https://www.cleverbot.com/getreply?key=${process.env.CleverApiKey}&input=${Question.slice(0).join(' ')}`,
							method : 'GET', parse : 'json'
						}).then(async (Result) => {
							Message.reply(Result.body.output, {
								allowedMentions : {
									repliedUser : false
								}
							})
						})
					}
				}
			}

            var Trigger = null
            this.Client.Database.query('SELECT * FROM reactions WHERE guild_id = $1', { bind : [ Message.guild.id ] }).then(async ([Results]) => {
                for (const Result of Results) {
                    if (Trigger && Result.trigger !== Trigger) return

                    if (String(Message.content).toLowerCase().includes(String(Result.trigger).toLowerCase())) {
                        Trigger = Result.trigger
                        await Message.react(Result.reaction)
                    }
                }
            })

            if (Message.mentions.members.first() && !this.Client.AFK.get(Message.author.id)) {
                const Away = this.Client.AFK.get(Message.mentions.members.first().id)
        
                if (Away) {
                    const [ Status, Created ] = Away
    
                    const Timestamp = await this.Client.CreateTimestamp(Created)
    
                    new this.Client.Response(
                        Message, `Member **${Message.mentions.members.first().user.tag}** has been set as **Away**: ${Status} - ${Timestamp} ago.`, {
                            Reply : true
                        }
                    )
                }
            }
            
            const Away = this.Client.AFK.get(Message.author.id)
    
            if (Away) {
                this.Client.AFK.delete(Message.author.id)
                Message.react('👋')
            }

            const Mention = GetMention(Message, this.Client)
            var ServerPrefix = this.Client.DefaultPrefix

            this.Client.Database.query(`SELECT * FROM prefixes WHERE guild_id = $1`, { bind : [ Message.guild.id ] }).then(async ([Results]) => {
                if (Results.length > 0) ServerPrefix = Results[0].prefix

                if (Mention || Message.content.startsWith(ServerPrefix)) {
                    const Arguments = Message.content.slice(Mention ? Mention.length : ServerPrefix.length).trim().split(/ +/g)
                    const Command = await this.Client.GetCommand(Arguments.shift().toLowerCase())

                    if (Command) {
                        const Structure = new this.Client.Structure(this.Client)
                        
                        Structure.Start(Message, Command, Arguments)
                    }
                }
            })
        } catch (Error) {
            return console.error(Error)
        }
    }
}

function GetMention (Message, Client) {
    const EscapeRegex = (String) => String.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    
    const MentionRegex = new RegExp(`^(<@!?${Client.user.id}> |${EscapeRegex('nick')})\\s*`)

    var Mention = null; 

    try { 
        [, Mention] = Message.content.toLowerCase().match(MentionRegex) 
    } catch (Error) {

    }

    return Mention
}