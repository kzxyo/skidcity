const { EmbedBuilder } = require("discord.js")

module.exports = class Case {
    constructor (Client, Message) {
        this.Client = Client
        this.Message = Message
    }

    async Insert (Moderator, Member, Action, Reason, Channel, Duration) {
        try {
            var Case = 0
            
            this.Client.Database.query(`SELECT * FROM history WHERE guild_id = ${this.Message.guild.id}`).then(async ([Results]) => {
                if (Results.length > 0) Case = Results.sort((a, b) => b.id - a.id)[0].id

                ++Case

                this.Client.Database.query(
                    `INSERT INTO history (guild_id, moderator_id, member_id, channel_id, action, reason, timestamp, duration, id) VALUES (${this.Message.guild.id}, ${Moderator.id}, ${Member === 'None' ? null : Member.id}, ${Channel === 'None' ? null : Channel.id}, '${Action}', '${Reason}', '${Math.floor(new Date().getTime() / 1000)}', '${Duration === 'None' ? null : Duration}', '${Case}')`
                )
            })

            this.Client.Database.query(`SELECT * FROM moderation_systems WHERE guild_id = ${this.Message.guild.id}`).then(async ([Results]) => {
                if (Results.length === 0) {
                    return new this.Client.Response(
                        this.Message, `Couldn't find a **Moderation Log** channel - Set one with the \`setup\` command.`
                    )
                }

                const Channel = this.Message.guild.channels.cache.get(Results[0].modlog_id)

                if (Channel) {
                    Channel.send({
                        embeds : [
                            new EmbedBuilder({
                                author : {
                                    name : `${Moderator.tag} (${Moderator.id})`,
                                    iconURL : Moderator.displayAvatarURL({
                                        dynamic : true
                                    })
                                },
                                description : `<t:${Math.floor(new Date().getTime() / 1000)}:F> (<t:${Math.floor(new Date().getTime() / 1000)}:R>)`,
                                fields : [
                                    {
                                        name : `Information (Case **#${Case}**)`,
                                        value : `**Action**: ${Action}\n**Member**: ${Member.tag} (${Member.id})\n**Reason**: ${Reason}`
                                    }
                                ]  
                            }).setColor(this.Client.Color)
                        ]
                    })
                }
            })
        } catch (Error) {
            return console.error(Error)
        }
    }
}