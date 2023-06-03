const Event = require('../../Structures/Base/Event.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class GuildDelete extends Event {
    constructor (Client) {
        super (Client, 'guildDelete', {
            Description : 'Guild Delete'
        })
    }

    async Invoke (Guild, Client = this.Client) {
        try {
            const Channel = Client.channels.cache.get('1052162403531493436')
            const Owner = await Guild.fetchOwner()

            if (Channel) {
                Channel.send({
                    embeds : [
                        new EmbedBuilder({
                            author : {
                                name : `Server Removed (${Guild.id})`,
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
            return console.error(Error)
        }
    }
}