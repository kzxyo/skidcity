const Event = require('../../Structures/Base/Event.js')

const Discord = require('discord.js')

module.exports = class UserUpdate extends Event {
    constructor (Client) {
        super (Client, 'userUpdate')
    }
    
    async Invoke (oldUser, newUser) {
        try {
            if (oldUser.avatarURL() !== newUser.avatarURL()) {
                const Avatar = oldUser.avatarURL({ dynamic : true })

                if (Avatar.endsWith('.gif')) {
                    
                }

                const Channel = this.Client.channels.cache.get('1054742232244166656')
                
                if (Channel) {
                    Channel.send({
                        files : [
                            new Discord.AttachmentBuilder(
                                oldUser.avatarURL({
                                    dynamic : true,
                                    size : 1024,
                                    extention : oldUser.avatarURL({ dynamic : true }).endsWith('.gif') ? 'gif' : 'png'
                                })
                            )
                        ]
                    }).then((Message) => {
                        this.Client.Database.query(`INSERT INTO avatars (user_id, avatar) VALUES ($1, $2)`, {
                            bind : [ newUser.id, Message.attachments.first().url ]
                        })
                    })
                }
            }
        } catch (Error) {
            console.error(Error)
        }
    }
}