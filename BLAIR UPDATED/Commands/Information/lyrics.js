const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

module.exports = class Lyrics extends Command {
    constructor (bot) {
        super (bot, 'lyrics', {})
    }

    async execute (bot, msg, args) {
        if (!args[0]) return msg.help()

        const Genius = require("genius-lyrics")
        const Client = new Genius.Client(process.env.GENIUS_ACCESS);

        const searches = await Client.songs.search(args.join(' '))
        console.log(searches[0])
        const song = searches[0]

        const lyrics = await searches[0].lyrics()

        const embeds = await Promise.all(lyrics.split('').list(800).map((x) => {
            x = x.join('').trim()
            const match = (text) => {
                return text.replace(/\[(.+?)\]/g, (match, p1) => {
                    return `**${p1}**:`
                })
            }

            x = match(x)

            return new Discord.EmbedBuilder({
                author: {
                    name : msg.member.displayName,
                    iconURL : msg.member.displayAvatarURL()
                },
                title : `${song.artist.name} - ${song.title}`,
                url : song.url,
                description:x,
                thumbnail : {
                    url : song.image
                }
            }).setColor(bot.colors.neutral)
        }))


        await new bot.paginator(
            msg, {
                embeds : embeds,
                iconURL : 'https://images.genius.com/2aa2941e1d8ed0034c2ddc9dd5012af9.1000x1000x1.png',
                text: `Genius ∙ Page {page} of {pages}`
            }
        ).construct()
    } 
}