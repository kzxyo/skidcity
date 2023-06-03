const Event = require('../../Structures/Base/Event.js')

const { Collection } = require('discord.js')
const Cooldown = new Collection()

module.exports = class VoiceStateUpdate extends Event {
    constructor (Client) {
        super (Client, 'voiceStateUpdate')
    }

    async Invoke (oldState, newState) {
        if (newState && newState.member && newState.channel) {
            this.Client.Database.query('SELECT * FROM voicemasters WHERE guild_id = $1', { bind : [ newState.guild.id ] }).then(async ([Results]) => {
                if (Results.length > 0) {
                    const JoinToCreate = await this.Client.channels.cache.get(Results[0].join_to_create)
                    const Category = await this.Client.channels.cache.get(Results[0].category)

                if (newState.channel.id === JoinToCreate.id) {
                        if (Cooldown.has(`VoiceMaster_${JoinToCreate.id}`)) {
                            return await newState.member.voice.setChannel(null, 'voicemaster: rate limit reached')
                        }

                        Cooldown.set(`VoiceMaster_${JoinToCreate.id}`, Date.now() + 10 * 1000)

                        setTimeout(() => {
                            Cooldown.delete(`VoiceMaster_${JoinToCreate.id}`)
                        }, 10 * 1000)

                        const VoiceChannel = await newState.guild.channels.create({
                            name : `${oldState.member.user.username}'s channel`,
                            type : 2,
                            parent : Category.id
                        })

                        await newState.member.voice.setChannel(VoiceChannel, 'voicemaster: join-to-create')
                    }
                }
            })
        }
    }
}