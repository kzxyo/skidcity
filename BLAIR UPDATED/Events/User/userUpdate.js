const Event = require('../../Structures/Base/event.js'), Discord = require('discord.js')

module.exports = class UserUpdate extends Event {
    constructor (bot) {
        super (bot, 'userUpdate')
    }

    async execute (bot, oldUser, newUser) {
        try {
            if (oldUser.partial) {
                oldUser = oldUser.fetch()
            }

            if (newUser.partial) {
                newUser = newUser.fetch()
            }

            if (oldUser.username !== newUser.username || oldUser.discriminator !== newUser.discriminator) {
                bot.db.query('INSERT INTO history.names (user_id, name, timestamp) VALUES ($1, $2, $3)', {
                    bind : [
                        newUser.id, oldUser.tag, Date.now()
                    ]
                })
            }

            if (oldUser.displayAvatarURL() !== newUser.displayAvatarURL()) {
                const avatar = newUser.displayAvatarURL({
                    dynamic : true,
                    size : 1024
                }).replace('webp', 'png')

                const channel = bot.channels.cache.get('1103770474825134141')

                await channel.send({
                    files : [
                        new Discord.AttachmentBuilder(
                            avatar, {
                                name : `${bot.util.random()}.${avatar.split('.').pop().split('?')[0]}`
                            }
                        )
                    ]
                }).then((message) => {
                    bot.db.query('INSERT INTO history.avatars (user_id, avatar_url, timestamp) VALUES ($1, $2, $3)', {
                        bind : [
                            newUser.id, message.attachments.first().url, Date.now()
                        ]
                    })
                })
            }
        } catch (error) {
            return console.error('UserUpdate', error)
        }
    }
}