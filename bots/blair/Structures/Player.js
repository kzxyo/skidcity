const DiscordPlayer = require('discord-player');

const { EmbedBuilder } = require('discord.js')
const Client = require('../blair.js');


const Player = new DiscordPlayer.Player(Client, {
    initialVolume : 100,
    autoSelfDeaf : false,
    ytdlOptions : {
        quality : 'highestaudio',
        highWaterMark : 1 << 25
    },
    disableVolume : false,
    spotifyBridge : true,
    bufferingTimeout : 0,
    leaveOnEmpty : false,
    leaveOnEmptyCooldown : 1000,
    leaveOnEnd : false,
    leaveOnStop : false
})

Player.on('trackStart', (Queue, Track) => {
    Queue.metadata.channel.send({
        embeds : [
            new EmbedBuilder({
                description : `Now Playing [${Track.title}](${Track.url}) in ${Queue.metadata.voice} - ${Track.requestedBy}`
            }).setColor(Client.Color)
        ]
    })
})

Player.on('queueEnd', async (Queue) => {
    setTimeout(() => {
        if (!Queue.playing) {
            Queue.metadata.guild.members.cache.get(Client.user.id).voice.setChannel(null)

            Queue.metadata.channel.send({
                embeds : [
                    new EmbedBuilder({
                        description : `Left ${Queue.metadata.voice} due to **3 Minutes** of inactivity.`
                    }).setColor(Client.Color)
                ]
            })

            Queue.destroy()
        }
    }, 180000)
})


module.exports = Player
