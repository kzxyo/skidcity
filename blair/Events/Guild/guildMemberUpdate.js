const Event = require('../../Structures/Base/Event.js') 

module.exports = class GuildMemberUpdate extends Event {
    constructor (Client) {
        super (Client, 'guildMemberUpdate')
    }

    async Invoke (oldMember, newMember) {
        try {
            if (oldMember.pending === true && newMember.pending === false) {
                this.Client.Database.query('SELECT * FROM welcomes WHERE guild_id = $1', { bind : [ newMember.guild.id ] }).then(async ([Results]) => {
                    for (const Result of Results) {
                        const Channel = newMember.guild.channels.cache.get(Result.channel_id)

                        const Content = new this.Client.Variables(Result.response)

                        const Response = await Content.Replace({ 
                            User : newMember.user, 
                            Member : newMember, 
                            Guild : newMember.guild
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