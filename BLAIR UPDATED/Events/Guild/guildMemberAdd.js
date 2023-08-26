const Event = require('../../Structures/Base/event.js')

module.exports = class GuildMemberAdd extends Event {
    constructor (bot) {
        super (bot, 'guildMemberAdd')
    }

    async execute (bot, member) {
        try {
            if (member.partial) {
                member = await member.fetch()
            }

            if (true) {
                const welcomes = await bot.db.query('SELECT * FROM system.welcomes WHERE guild_id = $1', {
                    bind : [
                        member.guild.id
                    ]
                }).then(([results]) => results)

                const promises = welcomes.map(async (welcome) => {
                    const channel = member.guild.channels.cache.get(welcome.channel_id)

                    if (channel) {
                        const message = new bot.MessageParser(
                            bot, await bot.variables.convert(
                                welcome.message, {
                                    user : member.user,
                                    member : member,
                                    guild : member.guild,
                                    channel : channel
                                }   
                            )
                        )
    
                        const sent = await channel.send(message)

                        if (welcome.self_destruct) {
                            setTimeout(() => {
                                sent.delete()
                            }, welcome.self_destruct * 1000)
                        }
                    }
                })

                await Promise.all(promises)
            }
        } catch (error) {
            console.error('Guild Member Add', error)
        }
    }
}