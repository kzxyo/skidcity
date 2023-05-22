const Event = require('../../Structures/Base/Event.js') 

module.exports = class GuildMemberAdd extends Event {
    constructor (Client) {
        super (Client, 'guildMemberAdd')
    }

    async Invoke (Member) {
        try {
            if (!Member.pending) {
                this.Client.Database.query('SELECT * FROM welcomes WHERE guild_id = $1', { bind : [ Member.guild.id ] }).then(async ([Results]) => {
                    for (const Result of Results) {
                        const Channel = Member.guild.channels.cache.get(Result.channel_id)

                        const Content = new this.Client.Variables(Result.response)

                        const Response = await Content.Replace({ 
                            User : Member.user, 
                            Member : Member, 
                            Guild : Member.guild
                        })

                        if (Channel) {
                            if (Result.response.startsWith('{embed}')) {
                                const Embed = new this.Client.EmbedParser(Response)

                                Channel.send(Embed).then(async (Message) => {
                                    if (Result.self_destruct) {
                                        setTimeout(() => {
                                            Message.delete()
                                        }, Result.self_destruct)
                                    }
                                })
                            } else {
                                Channel.send(Response).then(async (Message) => {
                                    if (Result.self_destruct) {
                                        setTimeout(() => {
                                            Message.delete()
                                        }, Result.self_destruct)
                                    }
                                })
                            }
                        }
                    }
                })
            }
        } catch (Error) {
            console.error(Error)
        }
    }
}