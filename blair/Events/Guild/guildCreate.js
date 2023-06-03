const Event = require('../../Structures/Base/Event.js')
const { EmbedBuilder } = require("discord.js")

module.exports = class GuildCreate extends Event {
    constructor (Client) {
        super (Client, 'guildCreate', {
            Description : 'Guild Create'
        })
    }

    async Invoke (Guild, Client = this.Client) {
        try {
            const Channel = Client.channels.cache.get('1052162403531493436')
            const Owner = await Guild.fetchOwner()

            if (Channel) {
                const Check = await Guild.fetchAuditLogs({ type: 80 }).then((Audit) => Audit.entries.first())
                const Inviter = Client.users.cache.get((Check.executor.id))

                Channel.send({
                    embeds : [
                        new EmbedBuilder({
                            author : {
                                name : `Server Added (${Guild.id})`,
                                iconURL : Guild.iconURL({
                                    dynamic : true
                                })
                            },
                            fields : [
                                {
                                    name : 'Server',
                                    value : `${Guild.name}`,
                                    inline : true
                                },
                                {
                                    name : 'Member Count',
                                    value : `${parseInt(Guild.memberCount).toLocaleString()}`,
                                    inline : true
                                },
                                {
                                    name : 'Inviter',
                                    value : `${Inviter.tag} (${Inviter.id})`,
                                    inline : true
                                }
                            ],
                            footer : {
                                text : `${Owner.user.tag} (${Owner.user.id})`
                            }
                        }).setColor(Client.Color).setTimestamp()
                    ]
                })
            }
        } catch (Error) {
            console.error(Error)
            return Guild.leave()
        }
    }
}